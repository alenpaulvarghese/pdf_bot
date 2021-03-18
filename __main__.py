from pyrogram import idle
from pdfbot import Pdfbot
import asyncio
import signal


if __name__ == "__main__":
    primary_engine = Pdfbot()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig, lambda sig=sig: loop.create_task(primary_engine.stop()))
    loop.create_task(primary_engine.start())
    idle()
