from pyrogram import Client, Filters
from plugins.pdfbot_locale import Phrase
from plugins.tools_bundle import is_encrypted, downloader, merger
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
            if (pdf.empty or pdf.from_user.is_self
                    or pdf.document is None
                    or pdf.document.mime_type != "application/pdf"):
                x -= 1
                merge_amount -= 1
                continue
            pdf_file_ids.append(pdf)
            merge_amount -= 1
        for_callback_filename = [Phrase.MERGE_APPROVE.format(
            num=len(pdf_file_ids)
            )]
        pdf_file_ids.reverse()
        for numbering, making_message in enumerate(pdf_file_ids):
            for_callback_filename.append(
               Phrase.MERGE_MESSAGE.format(
                    num=str(numbering+1),
                    filename=making_message.document.file_name
                    )
                )
        # https://stackoverflow.com/a/5618893/13033981
        output_message_final = ''.join(str(e) for e in for_callback_filename)
        await random_message.edit(text=output_message_final)
        await asyncio.sleep(3)
        file_names = []
        for number, files_in_this_list in enumerate(pdf_file_ids):
            await random_message.edit(
                text=f'Downloading {int(number)+1} of {len(pdf_file_ids)}'
                )
            await asyncio.sleep(1)
            filename, location = await downloader(
                files_in_this_list,
                files_in_this_list.document.file_name,
                client
            )
            file_names.append(filename)
        await random_message.edit(text='Download Finished')
        await random_message.edit(text='merging..')
        boolean, merged_file_name = await merger(
            file_names,
            message.message_id,
            location
        )
        if boolean:
            await random_message.edit(text='uploading..')
            await client.send_document(
                document=merged_file_name,
                chat_id=message.chat.id
            )
            await asyncio.sleep(4)
            os.remove(merged_file_name)
            await random_message.delete()
        elif not boolean:
            await random_message.edit(text=merged_file_name)
        for files in file_names:
            try:
                os.remove(files)
            except FileNotFoundError as e:
                pass
    else:
        await message.reply_text(text=Phrase.MERGE_NO)
