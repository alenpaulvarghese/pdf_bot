import logging


logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - [ %(message)s ]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOG_ = logging.getLogger("core")
