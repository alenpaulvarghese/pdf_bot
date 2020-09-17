from pyrogram import Client, filters
from plugins.pdfbot_locale import Phrase  # pylint:disable=import-error
from plugins.tools_bundle import downloader, merger, pdf_maker  # pylint:disable=import-error
import shutil
import asyncio


@Client.on_message(filters.command(["makepdf"]) & filters.private)
async def maker_cb(client, message):
    if (" " in message.text):
        _, maker = message.text.split(" ", 1)
        try:
            if int(maker) > 20:
                await message.reply_text(
                    Phrase.MERGE_HIGH.format(
                        num=maker
                    )
                )
                return
            elif int(maker) <= 0:
                await message.reply_text(text=Phrase.MERGE_LOW)
                return
        except ValueError:
            await message.reply_text(text=Phrase.INT_NOT_STR)
            return
        pdf_file_ids = []
        current_message_id = int(message.message_id)
        maker = int(maker)
        x, y = 1, 4
        random_message = await message.reply_text(text='Searching...')
        # complexity starting
        while x < maker+1 and y > 0:
            current_message_id -= 1
            memo = await client.get_messages(message.chat.id, current_message_id)
            if (memo.empty or memo.from_user.is_self):
                # or pdf.document.mime_type != "application/pdf"):
                if not memo.empty and not memo.from_user.is_self:
                    y -= 1
                x -= 1
                maker -= 1
                continue
            pdf_file_ids.append(memo)
            maker -= 1
        # complexity finished
        maker_list = []
        for _, each_message in enumerate(pdf_file_ids):
            if each_message.photo is not None:
                filename, location = await downloader(
                    each_message,
                    str(each_message.message_id),
                    client
                )
                pdf_page_name = pdf_maker(
                    filename,
                    f"{location}/{str(each_message.message_id)}.pdf"
                )
                maker_list.append(pdf_page_name)
            elif each_message.text is not None:
                pass
                # For Futureee
                # if not os.path.isdir('./FILES'):
                #     os.mkdir('./FILES')
                # location = f"./FILES/{str(each_message.chat.id)}/{str(each_message.message_id)}"
                # if not os.path.isdir(location):
                #     os.makedirs(location)
                # white_paper = Image.new("RGB", (595, 842), color="white")
                # draw = ImageDraw.Draw(white_paper)
                # font = ImageFont.truetype('./fonts/Roboto-Medium.ttf', 20)
                # draw.text((0, 0), each_message.text, font=font, align="center", fill="black")
                # paper_name = f"{location}/{str(each_message.message_id)}.jpeg"
                # white_paper.save(paper_name)

            else:
                pass
        if len(maker_list) <= 0:
            await random_message.edit(text=Phrase.MERGE_NO_PDF)
            return
        await random_message.edit(text='converting..')
        boolean, merged_file_name = await merger(
            maker_list,
            str(message.message_id),
            location,
            random_message
        )
        if boolean:
            await random_message.delete()
            random_message = await message.reply_text('Uploading..')
            await client.send_document(
                document=merged_file_name,
                chat_id=message.chat.id
            )
            await random_message.edit('<b>Succefully Uploaded</b>')
            await asyncio.sleep(10)
            try:
                shutil.rmtree(Phrase.LOCATION.format(loc=message.chat.id))
            except FileNotFoundError:
                pass
            await random_message.delete()
        elif not boolean:
            await random_message.edit(text=merged_file_name)
    else:
        await message.reply_text(text=Phrase.MERGE_NO)
