# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from tools.scaffold import PdfTask2
from pyrogram import Client
from plugins.logger import LOG_  # pylint:disable=import-error
import asyncio
import re


class Extractor(PdfTask2):
    def __init__(self, client: Client, chat_id: int, message_id: int, _range: str):
        super().__init__(client, chat_id, message_id)
        self.user_input = _range
        self.start_page = '0'
        self.end_page = '0'

    async def parse_input(self) -> bool:
        __pattern1__ = r"(^0*[1-9]{1}\d*)-(0*[1-9]{1}\d*$)"
        __pattern2__ = r"(^0*[1-9]\d*$)"
        if (match := re.search(__pattern1__, self.user_input)) is not None:
            start_page = match.group(1)
            end_page = match.group(2)
            if int(start_page) > int(end_page):
                await self.client.send_message(
                    chat_id=self.chat_id,
                    text="**start page is greater than end page**"
                )
            else:
                self.start_page, self.end_page = start_page, end_page
                return True
        elif (match := re.search(__pattern2__, self.user_input)) is not None:
            single = match.group(1)
            self.start_page, self.end_page = single, single
            return True
        await self.client.send_message(
            chat_id=self.chat_id,
            text="**failed to parse page range**"
        )
        return False

    async def process(self):
        pdf_check = await asyncio.create_subprocess_shell(
            f"qpdf --is-encrypted {self.input_file}"
        )
        if await pdf_check.wait() == 0:
            raise Exception("The given file is already encrypted")
        self.output = self.cwd + self.output
        cmd = [
            "pdftoppm",
            self.input_file,
            self.output,
            "-f", self.start_page,
            "-l", self.end_page,
            "-jpeg",
        ]
        self.output += "-1.jpg"
        LOG_.debug("exec: {}".format(" ".join(cmd)))
        proc = await asyncio.create_subprocess_shell(
            " ".join(cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if stderr:
            raise Exception(stderr.decode("utf-8"))
