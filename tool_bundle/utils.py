from typing import List
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

    async def file_allocator(self):
        """assign working directory for a task"""
        if not os.path.exists("./FILES"):
            os.mkdir("./FILES")
        proposed_cwd = f"./FILES/{self.chat_id}/"
        if not os.path.exists(proposed_cwd):
            os.mkdir(proposed_cwd)
        self.cwd = proposed_cwd
        await asyncio.sleep(0.001)

    async def find_files(self, file_id: int) -> Files:
        """find `File` objects in temp_files list usign file_id"""
        return [x for x in self.temp_files if x.file_id == file_id][0]
