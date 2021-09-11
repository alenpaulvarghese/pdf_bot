# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-


from typing import Dict, Optional
from tools import PdfTasks


class TaskPool(object):
    def __init__(self):
        self.__tasks__: Dict[int, PdfTasks] = dict()

    def add_task(self, chat_id: int, _task: PdfTasks) -> None:
        self.__tasks__[chat_id] = _task

    def get_task(self, chat_id: int) -> Optional[PdfTasks]:
        return self.__tasks__.get(chat_id)

    def remove_task(self, chat_id: int) -> None:
        self.__tasks__.pop(chat_id, None)

    def check_task(self, chat_id: int) -> bool:
        return chat_id in self.__tasks__
