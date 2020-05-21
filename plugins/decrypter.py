from pyrogram import Client, Filters
from plugins.tools_bundle import downloader, decrypter
from plugins.pdfbot_locale import Phrase
import asyncio
import shutil


@Client.on_message(Filters.command(["decrypt"]) & ~Filters.edited)
async def decrypter_cmd(client, message):
    # https://github.com/SpEcHiDe/AnyDLBot/blob/f112fc1e7ca72a6327fc0db68c049b096a588dac/plugins/rename_file.py#L45
    if (" " in message.text) and (message.reply_to_message is not None):
        cmd, password = message.text.split(" ", 1)
        if (message.reply_to_message.document is None or
                message.reply_to_message.document.mime_type != "application/pdf"):
            await message.reply_text(
                Phrase.NOT_PDF
            )
            return

        if len(password) > 60:
            await message.reply_text(
                Phrase.LONG_PASSWORD.format(
                    num=len(password)
                )
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
        await dwn.edit(text='Decrypting...')
        password_is_wrong, final_name = await decrypter(
            filename,
            password,
            location,
            message.message_id
            )
        if password_is_wrong:
            await dwn.edit(text=final_name)
            return
        if not password_is_wrong:
            await dwn.edit(text='Uploading...')
            await client.send_document(
                document=final_name,
                chat_id=message.chat.id
            )
            await dwn.edit('Succefully Uploaded')
            await asyncio.sleep(5)
            await dwn.delete()
        shutil.rmtree(Phrase.LOCATION.format(loc=message.chat.id))
    elif message.reply_to_message is None:
        await message.reply_text(
            Phrase.NO_REPLIED_MEDIA.format(
                method='decrypt'
            )
        )
        return
    elif (" " not in message.text):
        await message.reply_text(Phrase.DECRYPT_NO)
        return
