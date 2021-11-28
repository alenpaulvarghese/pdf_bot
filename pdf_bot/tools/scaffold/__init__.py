# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
import shutil
from pathlib import Path


class AbstractTask(object):
    def __init__(self, chat_id: int = 0, message_id: int = 0):
        # chat_id is used to identify each task message_id is used to allocate folders.
        self.chat_id = chat_id
        self.message_id = message_id
        # current working directory of the task.
        self.cwd: Path = self.file_allocator()
        # path for the output file.
        self.filename: str = "output.pdf"
        # future which tracks the completion of the task
        self.status: asyncio.Future = asyncio.get_running_loop().create_future()

    def file_allocator(self) -> Path:
        """assign working directory for a task."""
        path = Path(f"./FILES/{self.chat_id}/{self.message_id}")
        path.mkdir(parents=True, exist_ok=True)
        return path

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.chat_id})"

    def set_filename(self, name: str) -> None:
        self.filename = name

    def cleanup(self) -> None:
        shutil.rmtree(self.cwd)
