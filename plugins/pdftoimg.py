from pyrogram import Client, Filters
from plugins.tools_bundle import downloader, get_image_page
from plugins.pdfbot_locale import Phrase
import asyncio
import shutil


@Client.on_message(Filters.command(["extract"]) & ~Filters.edited)
async def pdftoimg_cmd(client, message):
    if(message.reply_to_message is not None):
        if (message.reply_to_message.document is None or
                message.reply_to_message.document.mime_type != "application/pdf"):
            await message.reply_text(
                Phrase.NOT_PDF
            )
            return
        if (" " in message.text):
            cmd, page_no = message.text.split(" ", 1)
            if('-' in page_no):
                page_range = page_no.split("-", 1)
                try:
                    page_start = int(page_range[0])
                    page_stop = int(page_range[1])
                    page_no = [page_start, page_stop]
                except ValueError:
                    print('Raised Value Error')
                    await message.reply_text(
                        Phrase.WRONG_FORMAT
                    )
                    return
            else:
                try:
                    page_no = int(page_no)
                except ValueError:
                    await message.reply_text(
                        Phrase.WRONG_FORMAT
                    )
                    return
        elif (" " not in message.text):
            page_no = None
        dwn = await message.reply_text("Downloading...", quote=True)
        filename, location = await downloader(
            message.reply_to_message,
            message.reply_to_message.document.file_name,
            client
            )
        await dwn.edit(text='Succefully Downloaded...')
        await asyncio.sleep(1.5)
        await dwn.edit(text='Extracting...')
        success, output_file = await get_image_page(
            filename,
            location,
            message.message_id,
            page_no,
        )
        await asyncio.sleep(2)
        if not success:
            await dwn.edit(text=output_file)
            return
        if success:
            await dwn.edit(text='Uploading...')
            if type(output_file) == list:
                sent_so_far = 0
                while sent_so_far <= len(output_file):
                    await client.send_chat_action(
                        message.chat.id,
                        "upload_photo"
                        )
                    await client.send_media_group(
                        media=output_file[sent_so_far:sent_so_far+10],
                        chat_id=message.chat.id
                    )
                    sent_so_far += 10
                    await asyncio.sleep(2)
            elif type(output_file) == str:
                await client.send_photo(
                        photo=output_file,
                        chat_id=message.chat.id
                    )
        await dwn.edit('Succefully Uploaded')
        await asyncio.sleep(5)
        await dwn.delete()
        #shutil.rmtree(Phrase.LOCATION.format(loc=message.chat.id))
    elif message.reply_to_message is None:
        await message.reply_text(
            Phrase.NO_REPLIED_MEDIA.format(
                method='convert pdf too image'
            )
        )
        return
