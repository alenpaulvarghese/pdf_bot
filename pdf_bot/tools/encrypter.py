# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
from pathlib import Path

from tools.scaffold import AbstractTask


class Encrypter(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        self.input_file: Path
        self.password: str = ""
        super().__init__(chat_id, message_id)

    def set_configuration(self, _path: Path, _pass: str) -> None:
        self.input_file = _path
        self.password = _pass

    async def process(self):
        pdf_check = await asyncio.create_subprocess_shell(
            f"qpdf --is-encrypted {self.input_file}"
        )
        if (await pdf_check.wait()) == 0:
            raise Exception("The given file is already encrypted")
        cmd = [
            "qpdf",
            "--encrypt",
            f"'{self.password}'",
            f"'{self.password}'",
            "128",
            "--",
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
