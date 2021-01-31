from pyrogram import Client
from creds import my
import asyncio

plugins = dict(root="plugins")


class Worker(Client):
    tasks = {}

    process_queue = []

    def __init__(self):
        super().__init__(
            "pdf bot",
            bot_token=my.BOT_TOKEN,
            api_id=my.API_ID,
            api_hash=my.API_HASH,
            plugins=plugins,
        )

    async def work(self):
        while True:
            while len(Worker.process_queue) != 0:
                for single_task in Worker.process_queue:
                    print(f"process_queue currently having {len(Worker.process_queue)} pending task")
                    await single_task.process()
                    single_task.status = 1
                    Worker.process_queue.remove(single_task)
                    await asyncio.sleep(5)
            else:
                await asyncio.sleep(1)
