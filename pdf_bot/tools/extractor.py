# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from tools.scaffold import AbstractTask
from itertools import groupby, count
from pathlib import Path
from typing import Set
import asyncio


class Extractor(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        super().__init__(chat_id, message_id)
        self.input_file: Path
        self.page_range: Set[int]

    def set_configuration(self, _path: Path, _range: Set[int]) -> None:
        self.input_file = _path
        self.page_range = _range

    async def process(self, _):
        # https://codereview.stackexchange.com/a/5202/244604
        _tcmd = ["pdftoppm", f"{self.input_file}", f"{self.cwd / 'output'}", "-jpeg"]
        grouped = [
            list(g)
            for _, g in groupby(self.page_range, lambda n, c=count(): n - next(c))
        ]
        for group in grouped:
            _args = None
            if len(group) >= 2:
                _args = ["-f", f"{group[0]}", "-l", f"{group[-1]}"]
            else:
                _args = ["-f", f"{group[0]}", "-l", f"{group[0]}"]
            proc = await asyncio.create_subprocess_shell(
                " ".join(_tcmd + _args),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if stderr:
                raise Exception(stderr.decode("utf-8"))
