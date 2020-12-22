from tool_bundle.utils import MakePdf, Files  # pylint:disable=import-error
from pyrogram import filters
from PIL import Image
from worker import Worker  # pylint:disable=import-error
from pyrogram.types import (
    Message,
    CallbackQuery,
    KeyboardButton,
    InputMediaPhoto,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import logging
import asyncio


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(10)


async def task_checker(_, __, message: Message) -> bool:
    if message.chat.id in Worker.tasks:
        return True
    else:
        return False


async def rotate_image(file_path: str, degree: int) -> str:
    """rotate images from input file_path and degree"""
    origin = Image.open(file_path)
    rotated_image = origin.rotate(degree, expand=True)
    await asyncio.sleep(0.001)
    rotated_image.save(file_path)
    LOGGER.debug(f"Image rotated and saved to --> {file_path}")
    return file_path


@Worker.on_message(filters.command(["make"]))
async def start(_, message: Message):
    await message.reply_text(
        "Now send me the photos",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton("Done"), KeyboardButton("Cancel")]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    new_task = MakePdf(message.chat.id, message.message_id)
    Worker.tasks[message.chat.id] = new_task
    await new_task.file_allocator()


@Worker.on_message()
async def explorer(_, message: Message):
    current_task = Worker.tasks.get(message.chat.id)
    if current_task is not None and message.photo:
        location = f"{current_task.cwd}/{message.message_id}.jpeg"
        await message.download(location)
        LOGGER.debug("download complete sending back image")
        current_task.temp_files.append(Files(message.message_id, location))
        await message.reply_photo(
            photo=location,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔄", f"{message.message_id}:rotate:90"),
                        InlineKeyboardButton("✅", f"{message.message_id}:insert"),
                        InlineKeyboardButton("❌", f"{message.message_id}:remove"),
                    ]
                ]
            ),
        )
        await message.delete()
    if message.text == "Cancel":
        if message.chat.id in Worker.tasks:
            Worker.tasks.pop(message.chat.id)
            LOGGER.debug("task deleted successfully")
        else:
            LOGGER.debug("task not found :ignoring:")
        await message.reply_text(
            "**Task cancelled**", reply_markup=ReplyKeyboardRemove()
        )
    if message.text == "Done":
        if current_task is None:
            await message.reply_text(
                "**Task Expired !**", reply_markup=ReplyKeyboardRemove()
            )
            return
        if len(current_task.proposed_files) == 0:
            await message.reply_text("No images found for processing")
            return
        await current_task.process()
    if message.document and (message.document.mime_type in ["image/png", "image/jpeg"]):
        pass


@Worker.on_callback_query()
async def callback_handler(_, callback: CallbackQuery):
    message: Message = callback.message
    current_task = Worker.tasks.get(message.chat.id)
    ext_id = int(callback.data.split(":", 1)[0])
    if current_task is None:
        await asyncio.gather(
            callback.answer("cancelled/timed-out"),
            message.delete(),
        )
        return
    if "rotate" in callback.data:
        degree = int(callback.data.split(":", 2)[2])
        file_path = (await current_task.find_files(ext_id)).path
        temporary_image = await rotate_image(file_path, degree)
        await message.edit_media(
            InputMediaPhoto(temporary_image), reply_markup=message.reply_markup
        )
    elif "insert" in callback.data:
        file_object = await current_task.find_files(ext_id)
        if file_object in current_task.temp_files:
            current_task.temp_files.remove(file_object)
        current_task.proposed_files.append(file_object)
        await asyncio.gather(
            message.delete(), message.reply_text("photo added successfully")
        )
        LOGGER.debug("image added to proposal queue")
    if "remove" in callback.data:
        file_object = await current_task.find_files(ext_id)
        if file_object in current_task.temp_files:
            current_task.temp_files.remove(file_object)
        await message.delete()
        LOGGER.debug("image removed from temporary queue")
