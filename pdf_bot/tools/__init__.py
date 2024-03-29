# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from typing import Union

from .decrypter import Decrypter
from .encrypter import Encrypter
from .extractor import Extractor
from .general import (
    mediagroup_generator,
    parse_range,
    rotate_image,
    slugify,
    task_checker,
)
from .makepdf import MakePdf
from .merge import Merge
from .rotate import RotatePdf
from .splitpdf import SplitPdf

PdfTasks = Union[MakePdf, Merge, Encrypter, Decrypter, Extractor, SplitPdf, RotatePdf]


__all__ = [
    "mediagroup_generator",
    "rotate_image",
    "task_checker",
    "parse_range",
    "Encrypter",
    "Decrypter",
    "Extractor",
    "RotatePdf",
    "SplitPdf",
    "PdfTasks",
    "MakePdf",
    "slugify",
    "Merge",
]
