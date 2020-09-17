from plugins.pdfbot_locale import Phrase  # pylint:disable=import-error
from pyrogram import Client, filters
from plugins.tools_bundle import check_size  # pylint:disable=import-error

API_PDF = ''


@Client.on_message(filters.command(["compress"]) & ~filters.edited)
async def compressor_cb(client, message):
    if (message.reply_to_message is not None):
        if (message.reply_to_message.document is None or
                message.reply_to_message.document.mime_type != "application/pdf"):
            await message.reply_text(
                Phrase.NOT_PDF
                )
            return
        elif await check_size(message.reply_to_message.document.file_size):
            await message.reply_text(
                Phrase.FILE_SIZE_HIGH
            )
            return
        await client.send_message(
            chat_id=message.chat.id,
            text='Choose the compression ratio',
            reply_markup=Phrase.COMPRESS_NAV,
            reply_to_message_id=message.reply_to_message.message_id
        )
    else:
        await message.reply_text(
            Phrase.NO_REPLIED_MEDIA.format(method="compress")
        )