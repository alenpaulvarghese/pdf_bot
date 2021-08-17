from tools import PdfTasks
import asyncio


class Worker(object):
    def __init__(self):
        self.worker_count = 2
        self.process_queue: asyncio.Queue[PdfTasks] = asyncio.Queue()

    async def start(self):
        for _ in range(self.worker_count):
            asyncio.create_task(self._worker())

    async def stop(self):
        for _ in range(self.worker_count):
            await self.process_queue.put(None)
        await self.process_queue.join()

    def new_task(self, task) -> asyncio.Future:
        self.process_queue.put_nowait(task)
        return task.status

    async def _worker(self):
        while True:
            task = await self.process_queue.get()
            try:
                if task is None:
                    break
                await task.process()
                task.status.set_result(0)
            except Exception as e:
                task.status.set_exception(e)
            finally:
                self.process_queue.task_done()
