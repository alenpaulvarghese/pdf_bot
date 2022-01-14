# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
import re
import traceback

from pdfbot import Pdfbot
from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import PhotoInvalidDimensions
from pyrogram.types import InputMediaDocument, InputMediaPhoto, Message
from tools import Extractor, mediagroup_generator, parse_range, task_checker


@Pdfbot.on_message(filters.command(["extract"]) & filters.create(task_checker))
async def extract_handler(client: Pdfbot, message: Message) -> None:
    if (
        message.reply_to_message is None
        or not message.reply_to_message.document
        or message.reply_to_message.document.mime_type != "application/pdf"
    ):
        await message.reply("Please reply to a PDF file")
        return
    task = client.new_task(Extractor, message.chat.id, message.message_id)
    if len(message.command) == 1:
        await message.reply("**usage:** `/extract page-range`")
        return
    if len(message.command) > 1:
        if message.command[1].startswith("-"):
            match = re.match(r"^\-r(\d+)$", message.command[1])
            if match is not None:
                task.set_resolution(int(match.group(1)))
            message.command.pop(1)
    status = await message.reply_text("__downloading...__")
    input_file = task.cwd / f"{message.reply_to_message.message_id}.pdf"
    await message.reply_to_message.download(input_file)
    await status.edit("__processing...__")
    try:
        page_range = parse_range(message.command[1])
        page_range.sort()
        task.set_configuration(input_file, set(page_range))
        await client.process_pool.new_task(task)
        try:
            image_list = [
                InputMediaPhoto(
                    str(task.cwd / f"output-{index}.jpg"), caption=f"page-{index}"
                )
                for index in task.page_range
            ]
            for media_group in mediagroup_generator(image_list):
                await asyncio.gather(
                    message.reply_chat_action("upload_photo"),
                    message.reply_media_group(
                        media_group,
                        disable_notification=True,
                    ),
                )
        except PhotoInvalidDimensions:
            doc_list = [
                InputMediaDocument(
                    str(task.cwd / f"output-{index}.jpg"), caption=f"page-{index}"
                )
                for index in task.page_range
            ]
            for media_group in mediagroup_generator(doc_list):
                await asyncio.gather(
                    message.reply_chat_action("upload_document"),
                    message.reply_media_group(
                        media_group,
                        disable_notification=True,
                    ),
                )

        await status.delete()
    except Exception as e:
        traceback.print_exc()
        await status.edit(f"**Task failed: `{e}`**")
    finally:
        task.cleanup()
        client.task_pool.remove_task(message.chat.id)
