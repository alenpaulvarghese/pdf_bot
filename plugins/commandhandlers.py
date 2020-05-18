from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup
from plugins.tools_bundle import pdf_silcer, is_encrypted , downloader
from plugins.pdfbot_locale import Phrase
import asyncio
import os


@Client.on_message(Filters.command(["start"]))
async def start(client, message):
    dwn = await message.reply_text(
                text='Choose any options',
                reply_markup=Phrase.HOME_NAV
    )


# @Client.on_message(Filters.document)
# async def downloader(client, message):
#     if message.document.mime_type == "application/pdf":
#         # Download and storing file
#         location = "./FILES" + "/" + str(message.chat.id)
#         if not os.path.isdir(location):
#             os.mkdir(location)
#         imgdir = location + "/" + message.document.file_name
#         dwn = await message.reply_text("Downloading...", quote=True)
#         await client.download_media(
#             message=message,
#             file_name=imgdir
#         )
#         # checking for file encryption
#         boolean = await is_encrypted(imgdir)
#         if boolean:
#             await dwn.edit(
#                 text='Choose any options',
#             )
#         else:
#             pass
#     else:
#         await message.reply(text='Oops This is not a pdf')


@Client.on_callback_query()
async def cb_(client, callback_query):
    cb_data = callback_query.data
    msg = callback_query.message
    if cb_data == 's&m':
        await msg.edit(
            text='Please Choose',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='Split PDF', callback_data='slicer')],
                [InlineKeyboardButton(text='Merge PDF', callback_data='merger')],
                [InlineKeyboardButton(text='back', callback_data='back')]
            ])
        )
    elif cb_data == 'pass':
        await msg.edit(
            text='Please Choose',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='encrypt', callback_data='encrypter')],
                [InlineKeyboardButton(text='decrypt', callback_data='decrypter')],
                [InlineKeyboardButton(text='back', callback_data='back')]
            ])
        )

    elif cb_data == 'compress':
        await msg.edit(
            text='Please Select Compresssion Ratio',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='low', callback_data='low')],
                [InlineKeyboardButton(text='recommended', callback_data='medium')],
                [InlineKeyboardButton(text='high', callback_data='high')]
            ])
        )
    elif cb_data == 'decrypter':
        await msg.edit(
            text=Phrase.DECRYPT_GUIDE,
            reply_markup=Phrase.BACK_MARKUP
        )
    elif cb_data == 'encrypter':
        await msg.edit(
            text=Phrase.ENCRYPT_GUIDE,
            reply_markup=Phrase.BACK_MARKUP
        )
    elif cb_data == 'low':
        await msg.edit(
            text=Phrase.COMPRESS_LOW
        )
    elif cb_data == 'medium':
        await msg.edit(
            text=Phrase.COMPRESS_MEDIUM
        )
    elif cb_data == 'high':
        await msg.edit(
            text=Phrase.COMPRESS_HIGH
        )
    elif cb_data == 'back':
        await msg.edit(
            text='Please Choose an option',
            reply_markup=Phrase.HOME_NAV
        )
        # print(callback_query)
        # await pdf_silcer(imgdir, int(callback_query.message.chat.id),
        #                 client, msg, str(callback_query.message.message_id))


@Client.on_message(Filters.command(["decrypt"]))
async def decrypter(client, message):
    # https://github.com/SpEcHiDe/AnyDLBot/blob/f112fc1e7ca72a6327fc0db68c049b096a588dac/plugins/rename_file.py#L45
    if (" " in message.text) and (message.reply_to_message is not None):
        cmd, password = message.text.split(" ", 1)
        if message.reply_to_message.document is None or message.reply_to_message.document.mime_type != "application/pdf":
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
        elif message.reply_to_message is None:
            await message.reply_text(
                Phrase.NO_REPLIED_MEDIA.format(
                    method='decrypt'
                )
            )
            return
        filename = await downloader(
            message.reply_to_message.chat.id, 
            message.reply_to_message.document.file_name,
            message,
            client
            )
        print(msg)
