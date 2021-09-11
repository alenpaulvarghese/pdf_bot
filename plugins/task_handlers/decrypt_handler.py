# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from tools import task_checker, slugify
from pyrogram.types import Message
from pyrogram import filters
from tools import Decrypter
from pdfbot import Pdfbot


@Pdfbot.on_message(filters.command(["decrypt"]) & filters.create(task_checker))
async def encrypt_handler(client: Pdfbot, message: Message) -> None:
    if message.reply_to_message is None or (
        message.document and message.document.mime_type != "document/pdf"
    ):
        await message.reply("Please reply to a PDF file")
        return
    if len(message.command) == 1:
        await message.reply("**usage:** `/decrypt password custom_file_name`")
        return
    status = await message.reply_text("**downloading...**")
    task = client.new_task(Decrypter, message.chat.id, message.message_id)
    if len(message.command) >= 3:
        filename = " ".join(message.command[2:])
        if len(filename) > 64:
            await message.reply_text("**WARNING:** file name too long, reducing...")
        filename = slugify(filename[:64])
        if filename in {".", "..", ".pdf"}:
            await message.reply_text(
                "**WARNING:** invalid filename falling back to default."
            )
        else:
            task.filename = filename
    input_file = task.cwd / f"{message.reply_to_message.message_id}.pdf"
    await message.reply_to_message.download(input_file)
    task.set_configuration(input_file, message.command[1])
    await status.edit("**processing...**")
    try:
        await client.process_pool.new_task(task)
        await message.reply_document(task.cwd / task.filename)
        await status.delete()
    except Exception as e:
        await status.edit(f"**Task failed: `{e}`**")
    finally:
        task.cleanup()
        client.task_pool.remove_task(message.chat.id)
