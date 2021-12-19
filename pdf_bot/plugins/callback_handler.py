# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio

from pdfbot import Pdfbot
from pyrogram import filters
from pyrogram.types import CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from tools import MakePdf, rotate_image


@Pdfbot.on_callback_query(filters.regex(r"insert|remove|rotate|^rm_task$|^del$"))
async def callback_handler(client: Pdfbot, callback: CallbackQuery):
    current_task = client.task_pool.get_task(callback.message.chat.id)
    if current_task is None:
        await asyncio.gather(
            callback.answer("cancelled/timed-out"),
            callback.message.delete(),
        )
        return
    elif callback.data == "rm_task":
        client.task_pool.remove_task(callback.message.chat.id)
        await asyncio.gather(
            callback.message.reply_text(
                "**Task** cancelled", reply_markup=ReplyKeyboardRemove()
            ),
            callback.message.delete(),
        )
        return
    elif callback.data == "del":
        await callback.message.delete()
        return

    file_id = int(callback.data.split(":", 1)[0])
    file_path = current_task.temp_files.get(file_id)
    if file_path is None:
        await asyncio.gather(
            callback.answer("cancelled/timed-out"),
            callback.message.delete(),
        )
    elif "rotate" in callback.data:
        await callback.answer("rotating please wait")
        degree = int(callback.data.split(":", 2)[2])
        temporary_image = await asyncio.get_event_loop().run_in_executor(
            None, rotate_image, file_path, degree
        )
        await callback.message.edit_media(
            InputMediaPhoto(temporary_image), reply_markup=callback.message.reply_markup
        )
    elif "insert" in callback.data:
        if file_path is not None:
            current_task.temp_files.pop(file_id)
            current_task.proposed_files.append(file_path)
            await callback.message.delete()
            if not current_task.quiet:
                await callback.message.reply_text(
                    text="photo added successfully"
                    if isinstance(current_task, MakePdf)
                    else "pdf added successfully"
                )
    elif "remove" in callback.data:
        current_task.temp_files.pop(file_id)
        await callback.message.delete()
