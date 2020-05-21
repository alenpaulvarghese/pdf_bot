import shutil
import asyncio
from plugins.pdfbot_locale import Phrase
from datetime import date
from pylovepdf.tools.compress import Compress
from pyrogram import Client, Filters

API_PDF = ''


@Client.on_message(Filters.command(["compress"]) & ~Filters.edited)
async def compressor_cb(client, message):
    if (message.reply_to_message is not None):
        if (message.reply_to_message.document is None or
                message.reply_to_message.document.mime_type != "application/pdf"):
            await message.reply_text(
                Phrase.NOT_PDF
                )
            return
        await client.send_message(
            chat_id=message.chat.id,
            text='Choose the compression ratio',
            reply_markup=Phrase.COMPRESS_NAV,
            reply_to_message_id=message.reply_to_message.message_id
        )
    else:
        await message.reply_text(
            Phrase.NO_REPLIED_MEDIA.format(method="compress")
        )