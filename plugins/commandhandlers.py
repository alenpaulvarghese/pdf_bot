from tool_bundle.utils import PdfTask, MakePdf, Merge  # pylint:disable=import-error
from pyrogram import filters
from worker import Worker  # pylint:disable=import-error
from PIL import Image
from pyrogram.types import (
    Message,
    CallbackQuery,
    KeyboardButton,
    InputMediaPhoto,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import logging
import asyncio


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(10)


async def task_checker(message: Message) -> bool:
    if message.chat.id in Worker.tasks:
        await message.reply_text(
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
        return True
    return False


async def rotate_image(file_path: str, degree: int) -> str:
    """rotate images from input file_path and degree"""
    origin = Image.open(file_path)
    rotated_image = origin.rotate(degree, expand=True)
    await asyncio.sleep(0.001)
    rotated_image.save(file_path)
    LOGGER.debug(f"Image rotated and saved to --> {file_path}")
    return file_path


@Worker.on_message(filters.command(["merge", "make"]))
async def merge(client: Worker, message: Message):
    if await task_checker(message):
        return
    is_merge = "merge" in message.command[0]
    await message.reply_text(
        f"Now send me the {'pdf files' if is_merge else 'photos'}",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton("Done"), KeyboardButton("Cancel")]],
            resize_keyboard=True,
        ),
    )
    new_task = (Merge if is_merge else MakePdf)(message.chat.id, message.message_id)
    Worker.tasks[message.chat.id] = new_task
    await asyncio.gather(
        new_task.file_allocator(),
        new_task.add_handlers(client),
    )
    if len(message.command) > 1:
        for commands in message.command[1:]:
            if commands.startswith("-"):
                if commands == "-q" or commands == "-quiet":
                    new_task.quiet = True
                elif commands == "-d" or commands == "-direct":
                    new_task.direct = True
            else:
                filename = commands
                if len(filename) > 64:
                    await message.reply_text(
                        "**WARNING:** file name too long, reducing..."
                    )
                    filename = filename[:64]
                if filename.endswith(".PDF") or filename.endswith(".pdf"):
                    filename = filename.replace(".PDF", "")
                    filename = filename.replace(".pdf", "")
                new_task.output = filename


@Worker.on_callback_query()
async def callback_handler(client: Worker, callback: CallbackQuery):
    message: Message = callback.message
    current_task: PdfTask = Worker.tasks.get(message.chat.id)
    if current_task is None:
        await asyncio.gather(
            callback.answer("cancelled/timed-out"),
            message.delete(),
        )
    elif (
        "rotate" in callback.data
        or "insert" in callback.data
        or "remove" in callback.data
    ):
        file_id = int(callback.data.split(":", 1)[0])
        file_path = current_task.temp_files.get(file_id)
        if file_path is None:
            await asyncio.gather(
                callback.answer("cancelled/timed-out"),
                message.delete(),
            )
        elif "rotate" in callback.data:
            degree = int(callback.data.split(":", 2)[2])
            temporary_image = await rotate_image(file_path, degree)
            await message.edit_media(
                InputMediaPhoto(temporary_image), reply_markup=message.reply_markup
            )
        elif "insert" in callback.data:
            if file_path is not None:
                current_task.temp_files.pop(file_id)
                current_task.proposed_files.append(file_path)
                await asyncio.gather(
                    message.delete(),
                    (
                        message.reply_text("photo added successfully")
                        if not current_task.quiet
                        else asyncio.sleep(0)
                    ),
                )
                LOGGER.debug("image added to proposal queue")
        elif "remove" in callback.data:
            current_task.temp_files.pop(file_id)
            await message.delete()
            LOGGER.debug("image removed from temporary queue")

    elif callback.data == "rm_task":
        Worker.tasks.pop(message.chat.id)
        await asyncio.gather(
            message.reply_text("**Task** cancelled", reply_markup=ReplyKeyboardRemove()),
            message.delete(),
        )
        message.reply_to_message.command = message.reply_to_message.text.split(" ")
        await merge(client, message.reply_to_message)

    elif callback.data == "del":
        await message.delete()
