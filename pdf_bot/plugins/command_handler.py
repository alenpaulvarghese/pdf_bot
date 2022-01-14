# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pdfbot import Pdfbot
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

__help__ = ["makepdf", "merge", "encrypt", "decrypt", "extract", "rotate", "split"]


# start command handler
@Pdfbot.on_message(filters.command(["start"]))
async def start_handler(client: Pdfbot, message: Message) -> None:
    if len(message.command) > 1 and message.command[1] in __help__:
        return_message = await message.reply_text("processing")
        await help_cbhandler(
            client,
            CallbackQuery(
                id=123,
                client=client,
                message=return_message,
                chat_instance="-1234",
                from_user=message.from_user,
                data=f"page-{str(__help__.index(message.command[1]))}",
            ),
        )
        return
    await message.reply(
        client.language["STRINGS"]["help"]["start"],
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("help", "page-help")]]
        ),
    )


@Pdfbot.on_message(filters.command("help") & filters.private)
async def _(client: Pdfbot, message: Message) -> None:
    return_message = await message.reply_text("processing")
    await help_cbhandler(
        client,
        CallbackQuery(
            id=123,
            client=client,
            message=return_message,
            chat_instance="-1234",
            from_user=message.from_user,
            data="page-help",
        ),
    )


@Pdfbot.on_callback_query(
    filters.create(lambda _, __, callback: "page" in callback.data),
    group=0,
)
async def help_cbhandler(client: Pdfbot, callback: CallbackQuery) -> None:
    if callback.data == "page-close":
        await callback.message.delete()

    elif callback.data == "page-help":
        await callback.message.edit(
            client.language["STRINGS"]["help"]["help"].format(
                bot=(await client.get_me()).username
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✖️", "page-close")]]
            ),
        )

    elif "page" in callback.data:
        _, next_page = callback.data.split("-")
        reply = InlineKeyboardMarkup([[], [InlineKeyboardButton("✖️", "page-close")]])
        if int(next_page) != 0:
            reply.inline_keyboard[0].append(
                InlineKeyboardButton("<<", f"page-{str(int(next_page)-1)}")
            )

        if not int(next_page) == len(__help__) - 1:
            reply.inline_keyboard[0].append(
                InlineKeyboardButton(">>", f"page-{str(int(next_page)+1)}")
            )

        await callback.message.edit(
            client.language["STRINGS"]["help"][__help__[int(next_page)]],
            reply_markup=reply,
        ),
    if not callback.id == 123:
        await callback.answer()
