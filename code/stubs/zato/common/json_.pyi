from typing import Any, TYPE_CHECKING

from datetime import date, timezone
from decimal import Decimal
from json import load, loads
from bson import ObjectId
from zato.common.typing_ import datetime_, datetimez
from ujson import dump, dumps as json_dumps
from json import dump, dumps as json_dumps

dump = dump
load = load
loads = loads
_utc = timezone.utc

def _default_handler(value: Any) -> None: ...

def dumps(data: Any, indent: Any = ...) -> None: ...
