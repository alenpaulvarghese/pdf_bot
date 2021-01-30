# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pyrogram.types import (
    Message,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters
from worker import Worker  # pylint:disable=import-error
from typing import List
from PIL import Image
import asyncio
import os


class Files(object):
    def __init__(self, file_id: int, path: str):
        self.file_id = file_id
        self.path = path

    def __del__(self):
        os.remove(self.path)


class PdfTask(object):
    def __init__(self, chat_id: int, message_id: int):
        self.chat_id = chat_id
        self.message_id = message_id
        self.cwd = None
        self.temp_files: List[Files] = []
        self.proposed_files: List[Files] = []
        self.output = "output"
        # 0-pending, 1-finished, 2-failed
        self.status = 0

    def __del__(self):
        for fs in self.temp_files + self.proposed_files:
            fs.__del__()
        if os.path.isfile(self.output):
            os.remove(self.output)

    async def file_allocator(self):
        """assign working directory for a task."""
        if not os.path.exists("./FILES"):
            os.mkdir("./FILES")
        proposed_cwd = f"./FILES/{self.chat_id}/"
        if not os.path.exists(proposed_cwd):
            os.mkdir(proposed_cwd)
        self.cwd = proposed_cwd
        await asyncio.sleep(0.001)

    async def find_files(self, file_id: int) -> Files:
        """find `File` objects in temp_files list using file_id."""
        data = [x for x in self.temp_files if x.file_id == file_id]
        if len(data) > 0:
            return data[0]

    async def add_handlers(self, client: Client) -> None:
        """add handler to Client according to the tasks."""
        client.add_handler(
            MessageHandler(
                PdfTask.command_handler,
                filters.text
                & filters.create(lambda _, __, m: m.chat.id in Worker.tasks),
            )
        )

    @staticmethod
    async def command_handler(_, message: Message):
        """custom handler made during task creation."""
        current_task = Worker.tasks.get(message.chat.id)
        if message.text == "Cancel":
            if message.chat.id in Worker.tasks:
                Worker.tasks.pop(message.chat.id)
            await message.reply_text(
                "**Task cancelled**", reply_markup=ReplyKeyboardRemove()
            )
        if message.text == "Done":
            if current_task is None:
                await message.reply_text(
                    "**Task Expired !**", reply_markup=ReplyKeyboardRemove()
                )
                return
            if len(current_task.proposed_files) == 0:
                await message.reply_text("No files found for processing")
                return


class MakePdf(PdfTask):
    def __init__(self, chat_id: int, message_id: int):
        super().__init__(chat_id, message_id)

    async def process(self):
        images: List[Image] = [Image.open(x.path) for x in self.proposed_files]
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
        current_task = Worker.tasks.get(message.chat.id)
        if current_task is not None and message.photo:
            location = f"{current_task.cwd}/{message.message_id}.jpeg"
            await message.download(location)
            current_task.temp_files.append(Files(message.message_id, location))
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
