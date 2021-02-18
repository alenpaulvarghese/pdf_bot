# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from tools.scaffold import PdfTask2
import asyncio


class Encrypter(PdfTask2):
    def __init__(self, chat_id: int, message_id: int, password: str):
        super().__init__(chat_id, message_id)
        self.user_input = password

    async def process(self):
        self.output = self.cwd + self.output + ".pdf"
        cmd = [
            "qpdf",
            "--encrypt",
            f"{self.user_input}",
            f"{self.user_input}",
            "128",
            "--",
            f"{self.input_file}",
            f"{self.output}",
        ]
        proc = await asyncio.create_subprocess_shell(
            " ".join(cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
