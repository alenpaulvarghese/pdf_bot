from pyrogram import Client, Filters
from plugins.pdfbot_locale import Phrase
from plugins.tools_bundle import is_encrypted, downloader
import os
import asyncio


@Client.on_message(Filters.command(["merge"]))
async def merger_cb(client, message):
    # print(pdf)
    if (" " in message.text):
        cmd, merge_amount = message.text.split(" ", 1)

        if int(merge_amount) > 10:
            await message.reply_text(
                Phrase.MERGE_HIGH.format(
                    num=merge_amount
                )
            )
            return
        pdf_file_ids = []
        current_message_id = int(message.message_id)
        merge_amount = int(merge_amount)
        x = 1
        random_message = await message.reply_text(text='Processing...')
        while x < merge_amount+1:
            current_message_id -= 1
            pdf = await client.get_messages(message.chat.id, current_message_id)
            if pdf.empty or pdf.from_user.is_self or pdf.document is None or pdf.document.mime_type != "application/pdf":
                x -= 1
                merge_amount -= 1
                continue
            pdf_file_ids.append(pdf)
            merge_amount -= 1
        pdf_file_ids.reverse()
        file_names = []
        for number, files_in_this_list in enumerate(pdf_file_ids):
            await random_message.edit(
                text=f'Downloading {int(number)+1} of {len(pdf_file_ids)}'
                )
            await asyncio.sleep(2)
            filename, location = await downloader(
                files_in_this_list,
                files_in_this_list.document.file_name,
                client
            )
            file_names.append(filename)
        await random_message.edit(text='Download Finished')
        print(file_names)
    else:
        await message.reply_text(text=Phrase.MERGE_NO)

