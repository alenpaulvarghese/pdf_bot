import asyncio
import re

from pdfbot import Pdfbot
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from tools import MakePdf, slugify, task_checker


@Pdfbot.on_message(filters.command("make") & filters.create(task_checker))
async def _(client: Pdfbot, message: Message):
    await message.reply_text(
        "Now send me the photos",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton("Done"), KeyboardButton("Cancel")]],
            resize_keyboard=True,
        ),
    )
    task = client.new_task(
        MakePdf,
        message.chat.id,
        message.message_id,
        MessageHandler(
            photo_handler,
            filters.photo
            & filters.create(
                lambda _, client, message: client.task_pool.check_task(message.chat.id)
            ),
        ),
    )
    if len(message.command) > 1:
        if message.command[1].startswith("-"):
            if re.match(r"^\-([qd]?[qd])$", message.command[1]) is not None:
                flags = message.command.pop(1)
                if "q" in flags:
                    task.quiet = True
                if "d" in flags:
                    task.interactive = False
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


async def photo_handler(client: Pdfbot, message: Message):
    """Handler to determine incoming photos under make task."""
    current_task = client.task_pool.get_task(message.chat.id)
    if current_task is not None and message.photo:
        location = current_task.cwd / f"{message.message_id}.jpeg"
        await message.download(location)
        if not current_task.interactive:
            current_task.proposed_files.append(location)
            await asyncio.gather(
                message.delete(),
                (
                    message.reply_text("photo added successfully")
                    if not current_task.quiet
                    else asyncio.sleep(0)
                ),
            )
        else:
            current_task.temp_files[message.message_id] = location
            await message.reply_photo(
                photo=location,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔄", f"{message.message_id}:rotate:90"
                            ),
                            InlineKeyboardButton("✅", f"{message.message_id}:insert"),
                            InlineKeyboardButton("❌", f"{message.message_id}:remove"),
                        ]
                    ]
                ),
            )
            await message.delete()
