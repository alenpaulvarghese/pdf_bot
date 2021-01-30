from worker import Worker
import asyncio


if __name__ == "__main__":
    primary_engine = Worker()
    primary_engine.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(primary_engine.work())
