import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    datefmt="[%Y-%m-%d %H:%M:%S %z]",
    force=True,
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("pikepdf").setLevel(logging.WARNING)
