# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Set

from poppler import PageRenderer, load_from_file

from tools.scaffold import AbstractTask


class Extractor(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        super().__init__(chat_id, message_id)
        self.input_file: Path
        self.page_range: Set[int]

    def set_configuration(self, _path: Path, _range: Set[int]) -> None:
        self.input_file = _path
        self.page_range = _range

    async def process(self):
        main_obj = load_from_file(self.input_file)
        last_page_range = max(self.page_range)
        if last_page_range > main_obj.pages:
            raise Exception(
                f"page range {last_page_range} is greater than total pages {main_obj.pages}"
            )
        page_render = PageRenderer()
        for index in self.page_range:
            render_obj = page_render.render_page(
                main_obj.create_page(index), xres=600, yres=600
            )
            render_obj.save(self.cwd / f"output-{index}.jpg", "jpeg")
            del render_obj
