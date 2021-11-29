# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pathlib import Path

import pikepdf

from tools.scaffold import AbstractTask


class Decrypter(AbstractTask):
    def __init__(self, chat_id: int, message_id: int):
        self.input_file: Path
        self.password: str = ""
        super().__init__(chat_id, message_id)

    def set_configuration(self, _path: Path, _pass: str) -> None:
        self.input_file = _path
        self.password = _pass

    def process(self):
        try:
            main_obj = pikepdf.open(self.input_file, password=self.password)
        except pikepdf._qpdf.PasswordError:
            raise Exception("Wrong password")
        if not main_obj.is_encrypted:
            raise Exception("File is not encrypted")
        main_obj.save(self.cwd / self.filename, encryption=False)
