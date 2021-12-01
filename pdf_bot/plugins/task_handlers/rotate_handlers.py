# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
import traceback

from pdfbot import Pdfbot
from pyrogram import filters
from pyrogram.types import Message
from tools import RotatePdf, parse_range, task_checker


@Pdfbot.on_message(filters.command(["rotate"]) & filters.create(task_checker))
async def extract_handler(client: Pdfbot, message: Message) -> None:
    if (
        message.reply_to_message is None
        or not message.reply_to_message.document
        or message.reply_to_message.document.mime_type != "application/pdf"
    ):
        await message.reply("Please reply to a PDF file")
        return
    if len(message.command) == 1:
        await message.reply("**usage:** `/rotate page-range`")
        return
    status = await message.reply_text("__downloading...__")
    task = client.new_task(RotatePdf, message.chat.id, message.message_id)
    rotate_angle = 90
    if len(message.command) == 3:
        try:
            rotate_angle = int(message.command[2])
        except ValueError:
            await message.reply_text(
                f"__Error: given degree {rotate_angle} is invalid__"
            )
            return
    input_file = task.cwd / f"{message.reply_to_message.message_id}.pdf"
    await message.reply_to_message.download(input_file)
    await status.edit("__processing...__")
    try:
        page_range = parse_range(message.command[1])
        page_range.sort()
        task.set_configuration(input_file, set(page_range), rotate_angle)
        await client.process_pool.new_task(task)
        await asyncio.gather(
            message.reply_chat_action("upload_document"),
            message.reply_document(
                task.cwd / task.filename,
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
