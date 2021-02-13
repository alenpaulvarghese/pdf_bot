from worker import Worker
import asyncio
import signal


async def shutdown(client: Worker):
    await client.stop()
    loop.stop()


if __name__ == "__main__":
    primary_engine = Worker()
    primary_engine.start()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig, lambda sig=sig: loop.create_task(shutdown(primary_engine))
        )
    loop.run_until_complete(primary_engine.work())
