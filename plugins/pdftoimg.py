from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
from plugins.tools_bundle import downloader, get_image_page  # pylint:disable=import-error
from plugins.pdfbot_locale import Phrase  # pylint:disable=import-error
from zipfile import ZipFile
import asyncio
import shutil


@Client.on_message(filters.command(["extract"]) & ~filters.edited)
async def pdftoimg_cmd(client, message):
    if(message.reply_to_message is not None):
        if (message.reply_to_message.document is None or
                message.reply_to_message.document.mime_type != "application/pdf"):
            await message.reply_text(
                Phrase.NOT_PDF
            )
            return
        if (" " in message.text):
            _, page_no = message.text.split(" ", 1)
            if('-' in page_no):
                page_range = page_no.split("-", 1)
                try:
                    page_start = int(page_range[0])
                    page_stop = int(page_range[1])
                    if page_start == 0 or page_stop == 0:
                        await message.reply_text(
                            Phrase.WRONG_FORMAT
                            )
                        return
                    page_no = [page_start, page_stop]
                except ValueError:
                    await message.reply_text(
                        Phrase.WRONG_FORMAT
                    )
                    return
            else:
                try:
                    page_no = int(page_no)
                    if page_no == 0:
                        await message.reply_text(
                            Phrase.WRONG_FORMAT
                                )
                        return
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
                if len(output_file) > 15:
                    await dwn.edit(text='<b>detected images more than 15\n\n<i>Zipping...</i></b>')
                    await asyncio.sleep(1)
                    # zipping if length is too high
                    zipped_file = f'{location}/extracted-aio_pdfbot.zip'
                    with ZipFile(zipped_file, 'w') as zipper:
                        for files in output_file:
                            zipper.write(files)
                    #  finished zipping and sending the zipped file as document
                    await dwn.edit(text='<b><i>uploading...</b></i>')
                    await client.send_chat_action(
                        message.chat.id,
                        "upload_document"
                        )
                    await client.send_document(
                        document=zipped_file,
                        chat_id=message.chat.id,
                        reply_to_message_id=message.reply_to_message.message_id
                        )
                else:
                    location_to_send = []
                    for count, images in enumerate(output_file, start=1):
                        location_to_send.append(InputMediaPhoto(
                            media=images,
                            caption='page-'+str(count)
                            ))
                    sent_so_far = 0
                    while sent_so_far <= len(location_to_send):
                        await client.send_chat_action(
                            message.chat.id,
                            "upload_photo"
                            )
                        await client.send_media_group(
                            media=location_to_send[sent_so_far:sent_so_far+10],
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
        try:
            shutil.rmtree(Phrase.LOCATION.format(loc=message.chat.id))
        except FileNotFoundError:
            pass
    elif message.reply_to_message is None:
        await message.reply_text(
            Phrase.NO_REPLIED_MEDIA.format(
                method='convert pdf too image'
            )
        )
        return
