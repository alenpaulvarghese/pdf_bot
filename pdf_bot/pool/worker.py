# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from concurrent.futures.thread import ThreadPoolExecutor
from tools.utils.exceptions import ServerShuttingDown
from typing import List, Optional
from tools import PdfTasks
import logging
import asyncio

_LOG = logging.getLogger(__name__)


class Worker(object):
    def __init__(self, thread_pool: ThreadPoolExecutor):
        self.worker_count = 2
        self.thread_pool = thread_pool
        self.running_processes: List[asyncio.Task] = []
        self.process_queue: asyncio.Queue[PdfTasks] = asyncio.Queue()

    def start(self, loop: asyncio.BaseEventLoop):
        for id in range(self.worker_count):
            loop.create_task(self._worker(), name=f"Process.Worker({id})")
        _LOG.info("Worker started with count of %d", self.worker_count)

    async def stop(self):
        _LOG.info("Shutting down worker")
        while self.process_queue.qsize() != 0:
            task = await self.process_queue.get()
            task.status.set_exception(ServerShuttingDown())
            self.process_queue.task_done()
        for ps in self.running_processes:
            _LOG.debug("\t - Cancelling running process %s", ps.get_name())
            ps.cancel()
        for _ in range(self.worker_count):
            await self.process_queue.put(None)
        await self.process_queue.join()

    def new_task(self, task) -> asyncio.Future:
        self.process_queue.put_nowait(task)
        return task.status

    async def _worker(self):
        while True:
            _task = await self.process_queue.get()
            _process: Optional[asyncio.Task] = None
            try:
                if _task is None:
                    break
                _process = asyncio.create_task(
                    _task.process(self.thread_pool),
                    name=_task.__repr__(),
                )
                self.running_processes.append(_process)
                await _process
                _task.status.set_result(0)
            except asyncio.CancelledError:
                _task.status.set_exception(ServerShuttingDown())
            except Exception as e:
                _task.status.set_exception(e)
            finally:
                if _process is not None:
                    self.running_processes.remove(_process)
                self.process_queue.task_done()
