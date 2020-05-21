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
    MERGE_NO_PDF = "Soory I couldn't find any PDF files.\nPlease checkout the guide to find how to merge PDF"
    MERGE_APPROVE = "<b>The following {num} PDF are going to be merged in the given order</b>\n\n"
    MERGE_MESSAGE = "<b>{num}.</b>  <code>{filename}</code>\n" 
    MERGE_CORRUPT = "The following file is corrupted or not a valid PDF file\n\n<code>{issue_with}</code>"
    INVALID_PASSWORD = "The following file is encrypted please use <b><code>/decrypt</code></b> command to decrypt the file\n\n<code>{issue_with}</code>"
    MERGE_ERR_LOG = "{time}\n\n issue: {issue}\n\n"
    INT_NOT_STR = "merge command is expecting a number not any other values"
    # https://github.com/SpEcHiDe/AnyDLBot/blob/f112fc1e7ca72a6327fc0db68c049b096a588dac/translation.py#L73
    RENAME_LONG_NAME = "File Name limit allowed by Telegram is 64 characters.The given file name has {num} characters.\n\n<b>Essays are not allowed in Telegram file name!\n\n</b>Please short your file name and try again!"
    RENAME_NO = "You didn't specified any name to rename"
    DECRYPT_NO = "You didn't specified any password to decrypt"
    ENCRYPT_NO = "You didn't specified any password to encrypt"
    MAIN_CORRUPT = "Soory the given file is corrupted or either invalid"
    WENT_WRONG = "soory something went wrong"
    LOCATION = "./FILES/{loc}"