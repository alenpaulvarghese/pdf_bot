# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pyrogram.types import Message, ReplyKeyboardRemove
from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters
from typing import Dict, List
import asyncio
import os


class GeneralTask(object):
    def __init__(self, client: Client = None, chat_id: int = 0, message_id: int = 0):
        # chat_id is used to identify each task message_id is used to allocate folders.
        self.chat_id = chat_id
        self.message_id = message_id
        # current working directory for each tasks ( will be allocated by method `file_allocator` ).
        self.cwd = ""
        # default filename for tasks.
        self.output = "output"
        # 0-pending, 1-finished, 2-failed
        self.status = 0
        # client object reference
        self.client: Client = client
        # string for identifying exceptions if there exist any.
        self.error_code = "something went wrong"

    async def file_allocator(self):
        """assign working directory for a task."""
        if not os.path.exists("./FILES"):
            os.mkdir("./FILES")
        proposed_cwd = f"./FILES/{self.chat_id}/"
        if not os.path.exists(proposed_cwd):
            os.mkdir(proposed_cwd)
        self.cwd = proposed_cwd
        await asyncio.sleep(0.001)


class PdfTask1(GeneralTask):
    def __init__(self, chat_id: int, message_id: int):
        # downloaded temporary files which are waiting for user confirmation to be added in proposed_files.
        self.temp_files: Dict[int, str] = {}
        # files that will be going to output.
        self.proposed_files: List[str] = []
        # quiet True if -q|-quiet flag is used else false; reduces info messages.
        self.quiet = False
        # for flag -d|-direct; send files directly to proposed queue without user approval.
        self.direct = False
        super().__init__(chat_id, message_id)

    def __del__(self):
        for files in list(self.temp_files.values()) + self.proposed_files:
            os.remove(files)
        self.proposed_files.clear()
        self.temp_files.clear()
        if os.path.isfile(self.output):
            os.remove(self.output)

    async def add_handlers(self, client: Client) -> None:
        """add handler to Client according to the tasks."""
        client.add_handler(
            MessageHandler(
                PdfTask1.command_handler,
                filters.text,
            ),
            group=0,
        )

    @staticmethod
    async def command_handler(client, message: Message):
        """custom handler made during task creation."""
        current_task = client.task_pool.get_task(message.chat.id)
        if message.text == "Cancel":
            client.task_pool.remove_task(message.chat.id)
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
            else:
                await message.reply_text(
                    "**processing...**",
                    reply_markup=ReplyKeyboardRemove(),
                )
                client.process_pool.new_task(current_task)
                while current_task.status == 0:
                    await asyncio.sleep(1.2)
                else:
                    if current_task.status == 2:
                        await message.reply_text(
                            f"**Task failed: `{current_task.error_code}`**"
                        )
                    elif current_task.status == 1:
                        await message.reply_document(current_task.output)
                        current_task.__del__()
                client.task_pool.remove_task(message.chat.id)


class PdfTask2(GeneralTask):
    def __init__(self, client: Client = None, chat_id: int = 0, message_id: int = 0):
        # input file send from client side
        self.input_file = ""
        # user input which includes password or page range
        self.user_input = ""

        super().__init__(client, chat_id, message_id)

    def __del__(self):
        for each_file in [self.input_file, self.output]:
            if os.path.exists(each_file):
                os.remove(each_file)

    async def allocate_and_download(self, message: Message):
        await self.file_allocator()
        self.input_file = await message.download(
            self.cwd + str(self.message_id) + ".pdf"
        )
