from typing import Dict, Any, Optional


class Task(object):
    def __init__(self):
        self.__tasks__: Dict[int, Any] = dict()

    def add_task(self, chat_id: int, _task: Any) -> None:
        self.__tasks__[chat_id] = _task

    def get_task(self, chat_id: int) -> Optional[Any]:
        return self.__tasks__.get(chat_id)

    def remove_task(self, chat_id: int) -> None:
        self.__tasks__.pop(chat_id, None)

    def check_task(self, chat_id: int) -> bool:
        print(self.__tasks__)
        return chat_id in self.__tasks__
