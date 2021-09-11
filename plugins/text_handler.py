from tools.makepdf import MakePdf
from tools.merge import Merge
from pyrogram.types import Message, ReplyKeyboardRemove
from pyrogram import filters
from pdfbot import Pdfbot


@Pdfbot.on_message(filters.regex(r"^Done$|^Cancel$"))
async def command_handler(client: Pdfbot, message: Message):
    """custom handler made during task creation that
    handles messages with text `Done` and `Cancel`."""
    current_task = client.task_pool.get_task(message.chat.id)
    if not isinstance(current_task, (MakePdf, Merge)):
        return
    if message.text == "Cancel":
        client.task_pool.remove_task(message.chat.id)
        await message.reply_text(
            "**Task cancelled**", reply_markup=ReplyKeyboardRemove()
        )
    if message.text == "Done":
        if len(current_task.proposed_files) == 0:
            await message.reply_text("No files found for processing")
            return
        else:
            client.task_pool.remove_task(message.chat.id)
            await message.reply_text(
                "**processing...**",
                reply_markup=ReplyKeyboardRemove(),
            )
            client.process_pool.new_task(current_task)
            try:
                await current_task.status
                await message.reply_document(current_task.cwd / current_task.filename)
            except Exception as e:
                import traceback

                traceback.print_exc()
                await message.reply_text(f"**Task failed: `{e}`**")
    current_task.cleanup()
    client.remove_handler(current_task.handler)
