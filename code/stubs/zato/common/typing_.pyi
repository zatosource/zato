from typing import Any, TYPE_CHECKING

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

from_dict = from_dict
optional = optional
Protocol = Protocol
TypedDict = TypedDict
intnone = optional[int]
strnone = optional[str]
anydict = dict_[any_, any_]
anydictnone = optional[anydict]
anylist = list_[any_]
anylistnone = optional[anylist]
anynone = optional[any_]
anyset = set_[any_]
anytuple = tuple_[any_, Any]
binaryio_ = binaryio_
boolnone = optional[bool]
byteslist = list_[bytes]
bytesnone = optional[bytes]
callable_ = callable_[Any, any_]
callnone = optional[callable_]
cast_ = cast_
commondict = dict_[str, Any]
commoniter = union_[anylist, anytuple]
date_ = date
datetime_ = datetime
datetimez = DateTimeWithZone
isotimestamp = _ISOTimestamp
decimal_ = decimal_
decnone = optional[decimal_]
dictlist = list_[anydict]
dictnone = optional[anydict]
dictorlist = union_[anydict, anylist]
dtnone = optional[datetime]
floatnone = optional[float]
generator_ = generator_
intanydict = dict_[int, any_]
intdict = dict_[int, int]
intdictdict = dict_[int, anydict]
intlist = list_[int]
intlistempty = list_[intnone]
intlistnone = optional[Any]
intset = set_[int]
intsetdict = dict_[int, anyset]
intstrdict = dict_[int, str]
iterator_ = iterator_
iobytes_ = io_[bytes]
listnone = anylistnone
listorstr = union_[anylist, str]
listtuple = tuple_[anylist, anylist]
model = type_[BaseModel]
modelnone = optional[Any]
module_ = ModuleType
noreturn = noreturn
path_ = Path
pathlist = list_[path_]
set_ = set_
stranydict = dict_[str, any_]
strcalldict = dict_[str, callable_]
strdict = stranydict
strbytes = union_[str_, bytes]
strbooldict = dict_[str, bool]
strcalldict = dict_[str, callable_]
strdictdict = dict_[str, anydict]
strdictlist = list_[stranydict]
strdictnone = union_[stranydict, Any]
strint = union_[str_, int]
strintbool = union_[str_, int, bool]
strintdict = dict_[str, int]
strintnone = union_[strnone, intnone]
strlist = list_[str]
strlistdict = dict_[str, anylist]
strlistempty = list_[strnone]
strlistnone = optional[Any]
strordict = union_[str, anydict]
strordictnone = union_[strnone, anydictnone]
strorfloat = union_[str, float]
stroriter = union_[str, anylist, anytuple]
strorlist = listorstr
strorlistnone = optional[listorstr]
strset = set_[str]
strsetdict = dict_[str, anyset]
strstrdict = dict_[str, str]
strtuple = tuple_[str, Any]
textio_ = textio_
textionone = textio_
tuple_ = tuple_
tuplist = union_[anylist, anytuple]
tupnone = optional[anytuple]
type_ = type_
typealias_ = typealias_
typevar_ = typevar_
union_ = union_

class _ISOTimestamp:
    ...

class DateTimeWithZone(datetime):
    ...

def instance_from_dict(class_: any_, data: anydict) -> any_: ...

def is_union(elem: any_) -> bool: ...

def extract_from_union(elem: any_) -> anytuple: ...

def list_field() -> callable_[anylist]: ...

def dict_field() -> callable_[anydict]: ...
