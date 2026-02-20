from typing import Any, TYPE_CHECKING

import os
from logging import Formatter
from zato.common.util.platform_ import is_posix
from zato.common.util.platform_ import is_linux


class ColorFormatter(Formatter):
    RESET_SEQ: Any
    COLOR_SEQ: Any
    BOLD_SEQ: Any
    COLORS: Any
    use_color: Any
    def __init__(self: Any, fmt: Any) -> None: ...
    def formatter_msg(self: Any, msg: Any, use_color: Any = ...) -> None: ...
    def format(self: Any, record: Any) -> None: ...

def get_logging_conf_contents() -> str: ...
