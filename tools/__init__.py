from .general import task_checker, slugify, parse_range, mediagroup_generator  # noqa
from .extractor import Extractor
from .encrypter import Encrypter
from .decrypter import Decrypter
from .splitpdf import SplitPdf
from .makepdf import MakePdf
from .merge import Merge
from typing import Union

PdfTasks = Union[MakePdf, Merge, Encrypter, Decrypter, Extractor, SplitPdf]
