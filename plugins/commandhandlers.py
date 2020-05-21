from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup
from plugins.tools_bundle import pdf_silcer, is_encrypted, downloader, decrypter, compressor
from plugins.pdfbot_locale import Phrase
import asyncio
import os
import shutil

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
    elif (cb_data == 'low') or (cb_data == 'extreme') or (cb_data == 'recommended'):
        await callback_query.message.edit(
            text='Downloading..'
        )
        file_name, location = await downloader(
            callback_query.message.reply_to_message,
            callback_query.message.reply_to_message.document.file_name,
            client
        )
        await callback_query.message.edit(
            text='Trying to compress..'
        )
        success, compressed_file = await compressor(
            cb_data,
            location,
            file_name
        )
        if success:
            await client.send_document(
                document=compressed_file,
                chat_id=callback_query.message.chat.id,
                caption="Compressed PDF"
            )
            await callback_query.message.delete()
            await asyncio.sleep(5)
            shutil.rmtree(Phrase.LOCATION.format(loc=callback_query.message.chat.id))
        elif not success:
            await random_message.edit(text=compressed_file)
    elif cb_data == 'back':
        await msg.edit(
            text='Please Choose an option',
            reply_markup=Phrase.HOME_NAV
        )
    elif cb_data == 'cancel':
        await msg.delete()
