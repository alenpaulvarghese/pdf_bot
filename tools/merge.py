# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters
from tools.scaffold import PdfTask1  # pylint:disable=import-error
from pikepdf import Pdf
from typing import List
import asyncio


class Merge(PdfTask1):
    def __init__(self, chat_id: int, message_id: int):
        super().__init__(chat_id, message_id)

    async def process(self):
        pdfs: List[Pdf] = [Pdf.open(x) for x in self.proposed_files]
        source = pdfs.pop(0)
        for pdf in pdfs:
            source.pages.extend(pdf.pages)
            await asyncio.sleep(0.1)
        self.output = self.cwd + self.output + ".pdf"
        source.save(self.output)

    async def add_handlers(self, client: Client) -> None:
        """add handler to Client according to the tasks."""
        await super().add_handlers(client)
        client.add_handler(
            MessageHandler(
                self.command_handler,
                filters.create(
                    lambda _, __, m: m.document
                    and m.document.mime_type == "application/pdf"
                )
                & filters.create(lambda _, client, message: client.task_pool.check_task(message.chat.id)),
            )
        )

    @staticmethod
    async def command_handler(client, message: Message):
        """handler to determine photos under make task."""
        current_task = client.task_pool.get_task(message.chat.id)
        if (
            current_task is not None
            and message.document
            and message.document.mime_type == "application/pdf"
        ):
            location = f"{current_task.cwd}{message.message_id}.pdf"
            await message.download(location)
            if current_task.direct:
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
