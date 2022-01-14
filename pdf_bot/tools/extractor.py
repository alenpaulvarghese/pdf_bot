# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Set

import fitz

from tools.scaffold import AbstractTask


class Extractor(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        super().__init__(chat_id, message_id)
        self.input_file: Path
        self.resolution = 400
        self.page_range: Set[int]

    def set_resolution(self, res: int) -> None:
        self.resolution = res

    def set_configuration(self, _path: Path, _range: Set[int]) -> None:
        self.input_file = _path
        self.page_range = _range

    def process(self):
        last_page_range = max(self.page_range)
        with fitz.Document(self.input_file) as main_obj:
            if last_page_range > len(main_obj):
                raise Exception(
                    f"page range {last_page_range} is greater than total pages {len(main_obj)}"
                )
            for index in self.page_range:
                render_obj = main_obj.load_page(index - 1)
                pix_obj = render_obj.get_pixmap(dpi=self.resolution)
                pix_obj.pil_save(self.cwd / f"output-{index}.jpg", optimize=True)
                del render_obj, pix_obj
        del main_obj, last_page_range
