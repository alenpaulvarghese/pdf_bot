import asyncio


class Worker(object):
    def __init__(self):
        self.worker_count = 2
        self.process_queue = asyncio.Queue()

    async def start(self):
        for _ in range(self.worker_count):
            asyncio.create_task(self._worker())

    async def stop(self):
        for _ in range(self.worker_count):
            self.new_task(None)
        await self.process_queue.join()

    def new_task(self, task):
        self.process_queue.put_nowait(task)

    async def _worker(self):
        while True:
            task = await self.process_queue.get()
            try:
                if task is None:
                    break

                await asyncio.get_running_loop().run_in_executor(task.process())
                task.status = 1
            except Exception as e:
                task.error_code = str(e)
                task.status = 2
            finally:
                self.process_queue.task_done()
                await asyncio.sleep(1)
                print("process finished")
