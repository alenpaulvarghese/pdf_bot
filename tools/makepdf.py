# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pyrogram.handlers import MessageHandler
from tools.scaffold import AbstractTask  # pylint:disable=import-error
from PIL import Image as ImageModule
from typing import List, Dict
from pathlib import Path
import asyncio


class MakePdf(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        # downloaded temporary files which are waiting for user confirmation to be added in proposed_files.
        self.temp_files: Dict[int, Path] = {}
        # files that will be going to output.
        self.proposed_files: List[Path] = []
        # for flag -q; reduces info messages.
        self.quiet: bool = False
        # for flag -i; send files directly to proposed queue without user approval.
        self.interactive: bool = True
        # handler used to register incoming media files.
        self.handler: MessageHandler = None

        super().__init__(chat_id, message_id)

    def set_handler(self, _handler: MessageHandler):
        self.handler = _handler

    async def process(self, executor):
        await asyncio.get_event_loop().run_in_executor(executor, self.process_executor)

    def process_executor(self):
        import time

        time.sleep(30)
        images: List[ImageModule.Image] = [
            ImageModule.open(x) for x in self.proposed_files
        ]
        primary = images.pop(0)
        primary.save(
            self.cwd / self.filename,
            "PDF",
            save_all=True,
            append_images=images,
            resolution=100.0,
        )
