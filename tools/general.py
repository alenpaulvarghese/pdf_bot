from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup


async def _task_checker(_, client, message: Message) -> bool:
    if client.task_pool.check_task(message.chat.id):
        await message.reply(
            "**cancel** existing task?",
            quote=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("yes", "rm_task"),
                        InlineKeyboardButton("no", "del"),
                    ]
                ]
            ),
        )
        return False
    return True
