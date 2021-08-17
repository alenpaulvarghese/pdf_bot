from tools import Merge, task_checker, slugify
from pyrogram.handlers import MessageHandler
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
)
from pdfbot import Pdfbot
import asyncio
import re


@Pdfbot.on_message(filters.command("merge") & filters.create(task_checker))
async def _(client: Pdfbot, message: Message):
    await message.reply_text(
        "Now send me the pdfs",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton("Done"), KeyboardButton("Cancel")]],
            resize_keyboard=True,
        ),
    )
    task = client.new_task(
        Merge,
        message.chat.id,
        message.message_id,
        MessageHandler(
            pdf_handler,
            filters.create(
                lambda _, __, m: m.document
                and m.document.mime_type == "application/pdf"
            )
            & filters.create(
                lambda _, client, message: client.task_pool.check_task(message.chat.id)
            ),
        ),
    )
    if len(message.command) > 1:
        if message.command[1].startswith("-"):
            if re.match(r"^\-([qi]?[qi])$", message.command[1]) is not None:
                flags = message.command.pop(1)
                if "q" in flags:
                    task.quiet = True
                if "i" in flags:
                    task.interactive = True
        filename = " ".join(message.command[1:])
        if filename == "":
            return
        elif len(filename) > 64:
            await message.reply_text("**WARNING:** file name too long, reducing...")
        filename = slugify(filename[:64])
        if filename in {".", "..", ".pdf"}:
            await message.reply_text(
                "**WARNING:** invalid filename falling back to default."
            )
        else:
            task.filename = filename


async def pdf_handler(client: Pdfbot, message: Message):
    """Handler to determine incoming pdfs under merge task."""
    current_task = client.task_pool.get_task(message.chat.id)
    if current_task is not None:
        location = current_task.cwd / f"{message.message_id}.pdf"
        await message.download(location)
        if not current_task.interactive:
            current_task.proposed_files.append(location)
            await asyncio.gather(
                message.delete(),
                (
                    message.reply_text("pdf added successfully")
                    if not current_task.quiet
                    else asyncio.sleep(0)
                ),
            )
            return
        current_task.temp_files[message.message_id] = location
        await message.reply_document(
            document=location,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✅", f"{message.message_id}:insert"),
                        InlineKeyboardButton("❌", f"{message.message_id}:remove"),
                    ]
                ]
            ),
        )
        await message.delete()
