import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [ %(message)s ]",
    datefmt="%d-%b-%y %H:%M:%S",
    force=True,
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
LOG_ = logging.getLogger("core")
