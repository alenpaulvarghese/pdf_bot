from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup
from plugins.tools_bundle import pdf_silcer, is_encrypted
from plugins.pdfbot_locale import Phrase
import asyncio
import os


@Client.on_message(Filters.command(["start"]))
async def start(client, message):
    dwn = await message.reply_text(
                text='Choose any options',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='Compress', callback_data='compress')],
                    [InlineKeyboardButton(text='Split and Merge', callback_data='s&m')],
                    [InlineKeyboardButton(text='PDF Protections', callback_data='pass')]
                ])
    )


@Client.on_message(Filters.document)
async def downloader(client, message):
    if message.document.mime_type == "application/pdf":
        # Download and storing file
        location = "./FILES" + "/" + str(message.chat.id)
        if not os.path.isdir(location):
            os.mkdir(location)
        imgdir = location + "/" + message.document.file_name
        dwn = await message.reply_text("Downloading...", quote=True)
        await client.download_media(
            message=message,
            file_name=imgdir
        )
        # checking for file encryption
        boolean = await is_encrypted(imgdir)
        if boolean:
            await dwn.edit(
                text='Choose any options',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='Compress', callback_data=f'compress')],
                    [InlineKeyboardButton(text='Split and Merge', callback_data=f's&m')],
                    [InlineKeyboardButton(text='PDF Protections', callback_data=f'pass')]
                ])
            )
        else:
            pass
    else:
        await message.reply(text='Oops This is not a pdf')


@Client.on_callback_query()
async def cb_(client, callback_query):
    cb_data = callback_query.data
    msg = callback_query.message
    if cb_data == 's&m':
        await msg.edit(
            text='Please Choose',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='Split PDF', callback_data='slicer')],
                [InlineKeyboardButton(text='Merge PDF', callback_data='merger')]
            ])
        )
    elif cb_data == 'pass':
        await msg.edit(
            text='Please Choose',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='encrypt', callback_data='encrypter')],
                [InlineKeyboardButton(text='decrypt', callback_data='decrypter')]
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
            text=Phrase.DECRYPT_GUIDE

        )
    elif cb_data == 'encrypter':
        await msg.edit(
            text=Phrase.ENCRYPT_GUIDE
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
        # print(callback_query)
        # await pdf_silcer(imgdir, int(callback_query.message.chat.id),
        #                 client, msg, str(callback_query.message.message_id))
