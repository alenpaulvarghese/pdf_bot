# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from pyrogram import filters
from pdfbot import Pdfbot  # pylint:disable=import-error


# start command handler
@Pdfbot.on_message(filters.command(["start"]))
async def start_handler(_, message: Message) -> None:
    await message.reply(
        "Hi 👋, I am a easy pdf utility bot\n\n"
        "**features:**\n"
        "~ Convert images to PDF\n"
        "~ Merge PDF files ",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("help", "page-0")]]),
    )


@Pdfbot.on_callback_query(
    filters.create(lambda _, __, callback: True if "page" in callback.data else False),
    group=0,
)
async def help_cbhandler(_, callback: CallbackQuery) -> None:
    if "page" in callback.data:
        _, next_page = callback.data.split("-")
        if next_page == "0":
            await callback.message.edit(
                """**Image to PDF**\n\n**command:** /make\n\n**flags:**\n
    `-d` : send files directly to queue without user approval.
    `-q` : reduce info messages\n
**Usage:**\n`/make [flags] custom_file_name`\n
**Example: **\n`/make -d -q WORK`""",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(">>", "page-1")]]
                ),
            )
        elif next_page == "1":
            await callback.message.edit(
                """**Merge PDF Files**\n\n**command:** /merge\n\n**flags:**\n
    `-d` : send files directly to queue without user approval.
    `-q` : reduce info messages\n
**Usage:**\n`/merge [flags] custom_file_name`\n
**Example: **\n`/merge -d -q MERGED_WORK`""",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("<<", "page-0")]]
                ),
            )
    await callback.answer()
