# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List

from pikepdf import Pdf

from tools.scaffold import AbstractTask


class RotatePdf(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        super().__init__(chat_id, message_id)
        self.input_file: Path
        self.degree: int = 90
        self.page_range: List[int]

    def set_configuration(self, _path: Path, _range: List[int], _degree: int) -> None:
        self.input_file = _path
        self.page_range = _range
        self.degree = _degree

    def process(self):
        with Pdf.open(self.input_file) as input_pdf:
            for index in self.page_range:
                input_pdf.pages[index - 1].rotate(self.degree, False)
            input_pdf.save(self.cwd / self.filename)
