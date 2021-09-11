from pyrogram.handlers.handler import Handler
from concurrent.futures import ThreadPoolExecutor
from pool import TaskPool, Worker
from pyrogram import Client
from typing import Optional
from logger import logging
from config import Config
from pathlib import Path
import asyncio
import signal
import yaml

_LOG = logging.getLogger(__name__)


class Pdfbot(Client):
    def __init__(self):
        super().__init__(
            session_name="pdf-bot",
            bot_token=Config.BOT_TOKEN,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins=dict(root="plugins"),
        )
        self.thread_pool = ThreadPoolExecutor(2)
        self.process_pool = Worker(self.thread_pool)
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

    def start(self):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        super().start()
        loop.run_in_executor(None, self.load_locale)
        self.process_pool.start(loop)
        _LOG.info("Client started")
        loop.run_forever()

    async def stop(self):
        await self.process_pool.stop()
        await super().stop()
        _LOG.info("Client Disconnected")
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
        asyncio.get_running_loop().stop()

    def load_locale(self):
        with open(Path("locale", "en.yaml"), "r") as f:
            self.language = yaml.load(f, Loader=yaml.CLoader)
        _LOG.info("Languages loaded")
