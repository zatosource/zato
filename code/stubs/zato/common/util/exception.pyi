from typing import Any, TYPE_CHECKING

from datetime import datetime
from traceback import TracebackException
from zato.common.version import get_version
from zato.common.typing_ import callnone


def pretty_format_exception(e: Exception, cid: str, utcnow_func: callnone = ...) -> str: ...
