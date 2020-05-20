# idea from https://github.com/SpEcHiDe/AnyDLBot/blob/master/translation.py
from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup

class Phrase(object):
    DECRYPT_GUIDE = '<b>Decrypt PDF using the following method</b>\n1. send the pdf file\n2. send the following command as a reply to the pdf file\n<code>/decrypt "passphrase"</code>'
    ENCRYPT_GUIDE = '<b>Encrypt PDF using the following method</b>\n1. send the pdf file\n2. send the following command as a reply to the pdf file\n<code>/encrypt "passphrase"</code>'
    COMPRESS_LOW = '<b>Compress PDF using the following method</b>\n[COMPRESSION RATIO : LOW]\n1. send the pdf file\n2. send the following command as a reply to the pdf file\n<code>/compress low</code>'
    COMPRESS_MEDIUM = '<b>Compress PDF using the following method</b>\n[COMPRESSION RATIO : MEDIUM]\n1. send the pdf file\n2. send the following command as a reply to the pdf file\n<code>/compress medium</code>'
    COMPRESS_HIGH = '<b>Compress PDF using the following method</b>\n[COMPRESSION RATIO : HIGH]\n1. send the pdf file\n2. send the following command as a reply to the pdf file\n<code>/compress high</code>'
    HOME_NAV = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='Compress', callback_data='compress')],
                    [InlineKeyboardButton(text='Split and Merge', callback_data='s&m')],
                    [InlineKeyboardButton(text='PDF Protections', callback_data='pass')],
                ])
    BACK_MARKUP = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='back', callback_data='back')]
    ])
    LONG_PASSWORD = 'Soory the password limit is 60 character. The given password is {num} character'
    NO_REPLIED_MEDIA = 'Please reply to a PDF to {method} it'
    NOT_PDF = "Soory this media is not a PDF"
    MERGE_HIGH = 'Soory the merge limit is 10 PDF. The given amount is {num} pdf'
    MERGE_LOW = 'Soory you at least need 2 PDF to merge'
    MERGE_NO = "You didn't specified any number of files to merge"
    MERGE_APPROVE = "<b>The following {num} PDF are going to be merged in the given order</b>\n\n"
    MERGE_MESSAGE = "<b>{num}.</b>  <code>{filename}</code>\n"
