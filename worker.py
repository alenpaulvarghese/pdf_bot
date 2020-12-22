from tool_bundle.utils import PdfTask
from pyrogram import Client
from typing import Dict
from creds import my

plugins = dict(root="plugins")


class Worker(Client):
    tasks: Dict[int, PdfTask] = {}

    def __init__(self):
        super().__init__(
            "pdf bot",
            bot_token=my.BOT_TOKEN,
            api_id=my.API_ID,
            api_hash=my.API_HASH,
            plugins=plugins,
        )
