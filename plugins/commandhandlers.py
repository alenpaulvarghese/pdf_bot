from tool_bundle.utils import MakePdf, PdfTask, Files  # pylint:disable=import-error
from pyrogram import Client, filters
from PIL import Image
from typing import List
from pyrogram.types import (
    Message,
    ForceReply,
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


_tasks_: List[PdfTask] = []


async def task_checker(_, __, message: Message) -> bool:
    for task in _tasks_:
        if task.chat_id == message.chat.id:
            return True
    return False


async def yield_task(chat_id: int) -> PdfTask:
    for task in _tasks_:
        if task.chat_id == chat_id:
            return task


async def rotate_image(file_path: str, degree: int) -> str:
    """rotate images from input file_path and degree"""
    origin = Image.open(file_path)
    rotated_image = origin.rotate(degree, expand=True)
    await asyncio.sleep(0.001)
    rotated_image.save(file_path)
    LOGGER.debug(f"Image rotated and saved to --> {file_path}")
    return file_path


@Client.on_message(filters.command(["make"]))
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
    global _tasks_
    _tasks_.append(new_task)
    await new_task.file_allocator()


@Client.on_message(filters.create(task_checker))
async def explorer(_, message: Message):
    current_task = await yield_task(message.chat.id)
    if message.text == "Cancel":
        global _tasks_
        if current_task in _tasks_:
            _tasks_.remove(current_task)
            LOGGER.debug("task deleted successfully")
        else:
            LOGGER.debug("task not found :ignoring:")
        await message.reply_text(
            "**Task cancelled**", reply_markup=ReplyKeyboardRemove()
        )
    if message.text == "Done":
        if len(current_task.proposed_files) == 0:
            await message.reply_text("No images found for processing")
            return
        await message.reply_text(
            "Now select one option.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Use default filename", "default"),
                        InlineKeyboardButton("Use custom filename", "custom"),
                    ]
                ]
            ),
        )
    if message.reply_to_message and ForceReply.__instancecheck__(
        message.reply_to_message.reply_markup
    ):
        current_task.output = message.text.replace("/", "").replace("\\", "")
        LOGGER.debug(f"set custom filename -> {current_task.output} >> now processing")
        await current_task.process()
    if message.photo:
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
    if message.document and (message.document.mime_type in ["image/png", "image/jpeg"]):
        pass


@Client.on_callback_query()
async def callback_handler(_, callback: CallbackQuery):
    message: Message = callback.message
    current_task = await yield_task(message.chat.id)
    if "custom" in callback.data or "default" in callback.data:
        if current_task is None:
            await message.reply_text("task timed-out/cancelled")
            LOGGER.debug("failed renaming > task missing")
            return
        if "custom" in callback.data:
            await asyncio.gather(
                message.reply_text(
                    "Reply the filename you want",
                    reply_markup=ForceReply(),
                ),
                message.delete(),
            )
        elif "default" in callback.data:
            await asyncio.gather(
                await message.delete(),
                await current_task.process(),
            )
        return
    ext_id = int(callback.data.split(":", 1)[0])
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
