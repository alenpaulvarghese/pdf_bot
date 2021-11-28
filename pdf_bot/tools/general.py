import asyncio
import re
from pathlib import Path
from typing import Iterator, List

from PIL import Image as ImageModule
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)


async def get_pages(path: Path) -> int:
    """Get total pages of a pdf file."""
    process = await asyncio.create_subprocess_shell(
        f"pdfinfo {path}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if stderr:
        raise Exception(stderr.decode("utf-8"))
    else:
        pages = re.search(r"^Pages: +(\d+)$", stdout.decode("utf-8"), re.MULTILINE)
        if pages is None:
            raise Exception("something went wrong")
        return int(pages.group(1))


def slugify(string) -> str:
    """
    Taken from https://github.com/django/django/blob/main/django/utils/text.py#L225,
    this modified function converts text into a valid filename.
    """
    string = string.strip().replace(" ", "_")
    string = re.sub(r"(?u)[^-\w.]", "", string)
    if not string.endswith(".pdf"):
        return re.sub(
            r"(?<!\.pdf)$",
            ".pdf",
            re.sub(r"\.[pP][dD][Ff]$", ".pdf", string),
        )
    return string


def rotate_image(file_path: Path, degree: int) -> Path:
    """Rotate image specified in file_path by given degree."""
    origin = ImageModule.open(file_path)
    rotated_image = origin.rotate(degree, expand=True)
    rotated_image.save(file_path)
    return file_path


async def task_checker(_, client, message: Message) -> bool:
    """Filter function used to check whether a task exist for the user."""
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


def mediagroup_generator(
    photos: List[InputMediaPhoto],
) -> Iterator[List[InputMediaPhoto]]:
    """Generator function that yields list of maximum 10 InputMediaPhoto"""
    for i in range(0, len(photos), 10):
        yield photos[i : i + 10]  # noqa: E203


def parse_range(input_string: str) -> List[int]:
    """Parser used to parse page-range from given string"""
    # matches hyphen seprated integers like (20-22)
    __pattern1__ = r"(^0*[1-9]{1}\d*)-(0*[1-9]{1}\d*$)"
    # matches a single integer like (20)
    __pattern2__ = r"(^0*[1-9]\d*$)"
    # matches comma seprated integers like (20,21,22,33)
    __pattern3__ = r"^(?:0*[1-9]{1}\d*,)+(?:0*[1-9]{1}\d*)?$"

    if (match := re.search(__pattern1__, input_string)) is not None:
        start_page = int(match.group(1))
        end_page = int(match.group(2))
        if start_page > end_page:
            raise Exception("Start page is greater than end page")
        else:
            return [x for x in range(start_page, end_page + 1)]

    elif (match := re.search(__pattern2__, input_string)) is not None:
        single = match.group(1)
        return [int(single)]

    elif (match := re.search(__pattern3__, input_string)) is not None:
        _range = []
        for _index in input_string.split(","):
            try:
                _range.append(int(_index))
            except ValueError:
                continue
        return _range
    raise Exception("Failed to parse page range")
