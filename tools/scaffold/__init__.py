from pyrogram.types import Message, ReplyKeyboardRemove
from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters
from typing import Dict, List
from worker import Worker  # pylint:disable=import-error
import asyncio
import os


class PdfTask(object):
    def __init__(self, chat_id: int, message_id: int):
        # chat_id is used to identify each task message_id is used to allocate folders.
        self.chat_id = chat_id
        self.message_id = message_id
        # current working directory for each tasks ( will be allocated by method `file_allocator` ).
        self.cwd = None
        # downloaded temporary files which are waiting for user confirmation to be added in proposed_files.
        self.temp_files: Dict[int, str] = {}
        # files that will be going to output.
        self.proposed_files: List[str] = []
        # default filename for tasks.
        self.output = "output"
        # 0-pending, 1-finished, 2-failed
        self.status = 0
        # string for identifying exceptions if there exist any.
        self.error_code = "something went wrong"
        # quiet True if -q|-quiet flag is used else false; reduces info messages.
        self.quiet = False
        # for flag -d|-direct; send files directly to proposed queue without user approval.
        self.direct = False

    def __del__(self):
        for files in list(self.temp_files.values()) + self.proposed_files:
            os.remove(files)
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

    async def add_handlers(self, client: Client) -> None:
        """add handler to Client according to the tasks."""
        client.add_handler(
            MessageHandler(
                PdfTask.command_handler,
                filters.text,
            ),
            group=0,
        )

    @staticmethod
    async def command_handler(_, message: Message):
        """custom handler made during task creation."""
        current_task: PdfTask = Worker.tasks.get(message.chat.id)
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
            else:
                await message.reply_text(
                    "**processing...**",
                    reply_markup=ReplyKeyboardRemove(),
                )
                Worker.process_queue.append(current_task)
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
