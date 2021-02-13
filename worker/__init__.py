from pyrogram import Client
from creds import my
import asyncio

plugins = dict(root="plugins")


class Worker(Client):
    tasks = {}

    process_queue = []

    def __init__(self):
        super().__init__(
            "pdf-bot",
            bot_token=my.BOT_TOKEN,
            api_id=my.API_ID,
            api_hash=my.API_HASH,
            plugins=plugins,
        )

    async def work(self):
        while True:
            while len(Worker.process_queue) != 0:
                for single_task in Worker.process_queue:
                    try:
                        await single_task.process()
                        single_task.status = 1
                    except Exception as e:
                        single_task.error_code = str(e)
                        single_task.status = 2
                    finally:
                        Worker.process_queue.remove(single_task)
                        Worker.tasks.pop(single_task.chat_id)
                        await asyncio.sleep(5)
                        print("process finished")
            else:
                await asyncio.sleep(1)
