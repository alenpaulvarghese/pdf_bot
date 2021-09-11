# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from tools.scaffold import AbstractTask
from typing import List
from pathlib import Path
from pikepdf import Pdf
import asyncio


class SplitPdf(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        super().__init__(chat_id, message_id)
        self.input_file: Path
        self.page_range: List[int]

    def set_configuration(self, _path: Path, _range: List[int]) -> None:
        self.input_file = _path
        self.page_range = _range

    async def process(self, executor):
        await asyncio.get_event_loop().run_in_executor(executor, self.process_executor)

    def process_executor(self):
        with Pdf.open(self.input_file) as input_pdf:
            with Pdf.new() as output_pdf:
                for index in self.page_range:
                    output_pdf.pages.append(input_pdf.pages[index - 1])
                output_pdf.save(self.cwd / self.filename)
