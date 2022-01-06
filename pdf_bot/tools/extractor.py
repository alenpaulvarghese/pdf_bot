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
        self.page_range: Set[int]

    def set_configuration(self, _path: Path, _range: Set[int]) -> None:
        self.input_file = _path
        self.page_range = _range

    def process(self):
        main_obj = fitz.Document(self.input_file)
        last_page_range = max(self.page_range)
        if last_page_range > main_obj.page_count:
            raise Exception(
                f"page range {last_page_range} is greater than total pages {main_obj.pages}"
            )
        for index in self.page_range:
            render_obj = main_obj.load_page(index)
            pix_obj = render_obj.get_pixmap(dpi=400)
            pix_obj.pil_save(
                self.cwd / f"output-{index}.jpg", optimize=True, dpi=(500, 500)
            )
            del render_obj, pix_obj
        main_obj.close()
        del main_obj, last_page_range
