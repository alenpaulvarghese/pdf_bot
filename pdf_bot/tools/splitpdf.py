# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from itertools import count, groupby
from pathlib import Path
from typing import List

import fitz

from tools.scaffold import AbstractTask


class SplitPdf(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        super().__init__(chat_id, message_id)
        self.input_file: Path
        self.page_range: List[int]

    def set_configuration(self, _path: Path, _range: List[int]) -> None:
        self.input_file = _path
        self.page_range = _range

    def process(self):
        # https://codereview.stackexchange.com/a/5202/244604
        grouped = [
            tuple(g)
            for _, g in groupby(self.page_range, lambda n, c=count(): n - next(c))
        ]
        with fitz.Document(self.input_file) as input_pdf:
            with fitz.Document() as output_pdf:
                for index, group in enumerate(grouped, 1):
                    final = 1 if index == len(grouped) else 0
                    output_pdf.insert_pdf(
                        input_pdf, group[0] - 1, group[-1] - 1, final=final
                    )
                output_pdf.save(self.cwd / self.filename, 3, 3, True)
