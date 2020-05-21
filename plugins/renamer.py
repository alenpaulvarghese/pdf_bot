from pyrogram import Client, Filters
from plugins.pdfbot_locale import Phrase
from plugins.tools_bundle import downloader
import os
import asyncio


@Client.on_message(Filters.command(["rename"]) & ~Filters.edited)
async def rename_cb(client, message):
    if (" " in message.text) and (message.reply_to_message is not None):
        cmd, file_rename_name = message.text.split(" ", 1)
        if (message.reply_to_message.document is None
                or message.reply_to_message.document.mime_type
                != "application/pdf"):
            await message.reply_text(
                Phrase.NOT_PDF
            )
            return
        # https://github.com/SpEcHiDe/AnyDLBot/blob/f112fc1e7ca72a6327fc0db68c049b096a588dac/plugins/rename_file.py#L47
        if len(file_rename_name) > 64:
            await message.reply_text(
                Phrase.RENAME_LONG_NAME.format(
                    num=len(file_rename_name)
                )
            )
            return
        if '.PDF' in file_rename_name:
            file_rename_name = file_rename_name.replace('.PDF', '.pdf')
        elif '.pdf' not in file_rename_name:
            file_rename_name += '.pdf'
        random_message = await message.reply_text("Downloading..")
        filename, location = await downloader(
            message.reply_to_message,
            file_rename_name,
            client
            )
        await random_message.edit(text='Uploading...')
        await client.send_document(
            document=filename,
            chat_id=message.chat.id
        )
        await asyncio.sleep(4)
        os.remove(filename)
        await random_message.delete()
    elif message.reply_to_message is None:
        await message.reply_text(
            Phrase.NO_REPLIED_MEDIA.format(
                method='rename'
            )
        )
        return
    elif (" " not in message.text):
        await message.reply_text(Phrase.RENAME_NO)
        return
