from typing import Any

from datetime import date, datetime
from decimal import Decimal as decimal_
from pathlib import Path
from types import ModuleType
from typing import Any as any_, BinaryIO as binaryio_, Callable as callable_, cast as cast_, Dict as dict_, Generator as generator_, Iterator as iterator_, IO as io_, NoReturn as noreturn, List as list_, Optional as optional, Text as str_, TextIO as textio_, Tuple as tuple_, Type as type_, TypeVar as typevar_, Set as set_, Union as union_
from dataclasses import *
from zato.common.marshal_.model import BaseModel
from typing_extensions import TypeAlias as typealias_
from dacite.core import from_dict
from typing import TypedDict
from typing import Protocol
from zato.common.ext.typing_extensions import TypedDict
from zato.common.ext.typing_extensions import Protocol

class _ISOTimestamp:
    ...

class DateTimeWithZone(datetime):
    ...

def instance_from_dict(class_: any_, data: anydict) -> any_: ...

def is_union(elem: any_) -> bool: ...

def extract_from_union(elem: any_) -> anytuple: ...

def list_field() -> callable_[anylist]: ...

def dict_field() -> callable_[anydict]: ...
