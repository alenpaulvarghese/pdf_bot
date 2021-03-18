from pool import Task, Worker
from pyrogram import Client
from creds import my


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
        self.task_pool = Task()

    async def start(self):
        await super().start()
        await self.process_pool.start()

    async def stop(self):
        await self.process_pool.stop()
        await super().stop()
