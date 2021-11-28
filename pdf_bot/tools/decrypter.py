# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
from pathlib import Path

from tools.scaffold import AbstractTask


class Decrypter(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        self.input_file: Path
        self.password: str = ""
        super().__init__(chat_id, message_id)

    def set_configuration(self, _path: Path, _pass: str) -> None:
        self.input_file = _path
        self.password = _pass

    async def process(self):
        cmd = [
            "qpdf",
            f"--password={self.password}",
            "--decrypt",
            f"{self.input_file}",
            f"{self.cwd / self.filename}",
        ]
        proc = await asyncio.create_subprocess_shell(
            " ".join(cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if stderr:
            raise Exception(stderr.decode("utf-8"))
