from pyrogram.handlers.handler import Handler
from pool import TaskPool, Worker
from pyrogram import Client
from typing import Optional
from logger import logging
from creds import my
import yaml

_LOG = logging.getLogger(__name__)


class Pdfbot(Client):
    def __init__(self):
        super().__init__(
            session_name="pdf-bot",
            bot_token=my.BOT_TOKEN,
            api_id=my.API_ID,
            api_hash=my.API_HASH,
            plugins=dict(root="plugins"),
        )
        self.process_pool = Worker()
        self.task_pool = TaskPool()
        self.languages: dict = {}

    def new_task(
        self,
        _type,
        chat_id: int,
        message_id: int,
        handler: Optional[Handler] = None,
    ):
        task = _type(chat_id, message_id)  # type: ignore
        if handler:
            task.set_handler(handler)
            self.add_handler(handler)
        self.task_pool.add_task(chat_id, task)
        return task

    async def start(self):
        with open("locale/en.yaml", "r") as f:
            self.language = yaml.load(f, Loader=yaml.CLoader)
        await super().start()
        await self.process_pool.start()
        _LOG.info("Client started")

    async def stop(self):
        await self.process_pool.stop()
        await super().stop()
