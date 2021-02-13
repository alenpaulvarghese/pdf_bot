# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters
from scaffold import PdfTask1  # pylint:disable=import-error
from worker import Worker  # pylint:disable=import-error
from typing import List
from PIL import Image
import asyncio


class MakePdf(PdfTask1):
    def __init__(self, chat_id: int, message_id: int):
        super().__init__(chat_id, message_id)

    async def process(self):
        images: List[Image] = [Image.open(x) for x in self.proposed_files]
        self.output = self.cwd + self.output + ".pdf"
        primary = images.pop(0)
        await asyncio.sleep(0.001)
        primary.save(
            self.output,
            "PDF",
            save_all=True,
            append_images=images,
            resolution=100.0,
        )

    async def add_handlers(self, client: Client) -> None:
        """add handler to Client according to the tasks."""
        await super().add_handlers(client)
        client.add_handler(
            MessageHandler(
                self.command_handler,
                filters.photo
                & filters.create(lambda _, __, m: m.chat.id in Worker.tasks),
            )
        )

    @staticmethod
    async def command_handler(_, message: Message):
        """handler to determine photos under make task."""
        current_task: MakePdf = Worker.tasks.get(message.chat.id)
        if current_task is not None and message.photo:
            location = f"{current_task.cwd}{message.message_id}.jpeg"
            await message.download(location)
            if current_task.direct:
                current_task.proposed_files.append(location)
                await asyncio.gather(
                    message.delete(),
                    (
                        message.reply_text("photo added successfully")
                        if not current_task.quiet
                        else asyncio.sleep(0)
                    ),
                )
                return
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
