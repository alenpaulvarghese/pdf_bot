# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pyrogram.handlers import MessageHandler
from tools.scaffold import AbstractTask
from typing import List, Dict
from pikepdf import Pdf
from pathlib import Path
import asyncio


class Merge(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        # downloaded temporary files which are waiting for user confirmation to be added in proposed_files.
        self.temp_files: Dict[int, Path] = {}
        # files that will be going to output.
        self.proposed_files: List[Path] = []
        # for flag -q; reduces info messages.
        self.quiet: bool = False
        # for flag -i; send files directly to proposed queue without user approval.
        self.interactive: bool = False
        # handler used to register incoming media files.
        self.handler: MessageHandler = None

        super().__init__(chat_id, message_id)

    def set_handler(self, _handler: MessageHandler):
        self.handler = _handler

    async def process(self, executor):
        try:
            await asyncio.get_event_loop().run_in_executor(
                executor, self.process_executor
            )
        except asyncio.CancelledError:
            raise Exception("Server Shutting down, try again later")

    def process_executor(self):
        from time import sleep

        sleep(30)
        with Pdf.open(self.proposed_files.pop(0)) as init_pdf:
            for paths in self.proposed_files:
                with Pdf.open(paths) as extension:
                    init_pdf.pages.extend(extension.pages)
            init_pdf.save(self.cwd / self.filename)
