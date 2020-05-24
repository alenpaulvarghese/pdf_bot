from pyrogram import Client, Filters
from plugins.tools_bundle import downloader, get_image_page
from plugins.pdfbot_locale import Phrase
import asyncio
import shutil


@Client.on_message(Filters.command(["extract"]) & ~Filters.edited)
async def pdftoimg_cmd(client, message):
    if (" " in message.text) and (message.reply_to_message is not None):
        cmd, password = message.text.split(" ", 1)
        if (message.reply_to_message.document is None or
                message.reply_to_message.document.mime_type != "application/pdf"):
            await message.reply_text(
                Phrase.NOT_PDF
            )
            return
        dwn = await message.reply_text("Downloading...", quote=True)
        filename, location = await downloader(
            message.reply_to_message,
            message.reply_to_message.document.file_name,
            client
            )
        await dwn.edit(text='Succefully Downloaded...')
        await asyncio.sleep(1.5)
        await dwn.edit(text='Extracting...')
        output_file = await get_image_page(
            filename,
            location+'/extracted'+str(message.message_id)+'.jpeg',
            int(password),
            1,
        )
        await asyncio.sleep(1.5)
        await dwn.edit(text='Uploading...')
        await client.send_photo(
            photo=output_file,
            chat_id=message.chat.id
        )
        await dwn.edit('Succefully Uploaded')
        await asyncio.sleep(5)
        await dwn.delete()
        shutil.rmtree(Phrase.LOCATION.format(loc=message.chat.id))
    elif message.reply_to_message is None:
        await message.reply_text(
            Phrase.NO_REPLIED_MEDIA.format(
                method='extract'
            )
        )
        return
    elif (" " not in message.text):
        await message.reply_text(Phrase.DECRYPT_NO)
        return
