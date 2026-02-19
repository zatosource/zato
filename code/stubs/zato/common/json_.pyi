from typing import Any

from datetime import date, timezone
from decimal import Decimal
from json import load, loads
from bson import ObjectId
from zato.common.typing_ import datetime_, datetimez
from ujson import dump, dumps as json_dumps
from json import dump, dumps as json_dumps

def _default_handler(value: Any) -> None: ...

def dumps(data: Any, indent: Any = ...) -> None: ...
