# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# stdlib
from datetime import date, datetime
from decimal import Decimal as decimal_
from pathlib import Path
from types import ModuleType
from typing import           \
    Any as any_,             \
    BinaryIO as binaryio_,   \
    Callable as callable_,   \
    cast as cast_,           \
    Dict as dict_,           \
    Generator as generator_, \
    Iterator as iterator_,   \
    IO as io_,               \
    NoReturn as noreturn,    \
    List as list_,           \
    Optional as optional,    \
    Text as str_,            \
    TextIO as textio_,       \
    Tuple as tuple_,         \
    Type as type_,           \
    TypeVar as typevar_,     \
    Set as set_,             \
    Union as union_

# typing-extensions
try:
    from typing_extensions import \
        TypeAlias as typealias_ # type: ignore
except Exception:
    typealias_ = None

# dacite
try:
    from dacite.core import from_dict
except Exception:
    from_dict = None

# stdlib
from dataclasses import * # type: ignore

# Zato
from zato.common.marshal_.model import BaseModel

# ################################################################################################################################
# ################################################################################################################################

#
# TypedDict
#
try:
    from typing import TypedDict
    from typing import Protocol
except ImportError:
    from zato.common.ext.typing_extensions import TypedDict
    from zato.common.ext.typing_extensions import Protocol

# ################################################################################################################################
# ################################################################################################################################

# For flake8
from_dict = from_dict
optional  = optional
Protocol  = Protocol
TypedDict = TypedDict

# ################################################################################################################################
# ################################################################################################################################

class _ISOTimestamp:
    pass

class DateTimeWithZone(datetime):
    pass

# ################################################################################################################################
# ################################################################################################################################

# Some basic types are defined upfront to make sure that none of the later definitions results in the type "Unknown".
intnone       = optional[int]
strnone       = optional[str]

anydict       = dict_[any_, any_]
anydictnone   = optional[anydict]
anylist       = list_[any_]
anylistnone   = optional[anylist]
anynone       = optional[any_]
anyset        = set_[any_]
anytuple      = tuple_[any_, ...]
binaryio_     = binaryio_
boolnone      = optional[bool]
byteslist     = list_[bytes]
bytesnone     = optional[bytes]
callable_     = callable_[..., any_]
callnone      = optional[callable_]
cast_         = cast_
commondict    = dict_[str, union_[int, str_, bool, float, anydict, anylist, datetime, None]]
commoniter    = union_[anylist, anytuple]
date_         = date
datetime_     = datetime
datetimez     = DateTimeWithZone
isotimestamp  = _ISOTimestamp
decimal_      = decimal_
decnone       = optional[decimal_]
dictlist      = list_[anydict]
dictnone      = optional[anydict]
dictorlist    = union_[anydict, anylist]
dtnone        = optional[datetime]
floatnone     = optional[float]
generator_    = generator_
intanydict    = dict_[int, any_]
intdict       = dict_[int, int]
intdictdict   = dict_[int, anydict]
intlist       = list_[int]
intlistempty  = list_[intnone]
intlistnone   = optional[list_[int]]
intset        = set_[int]
intsetdict    = dict_[int, anyset]
intstrdict    = dict_[int, str]
iterator_     = iterator_
iobytes_      = io_[bytes]
listnone      = anylistnone
listorstr     = union_[anylist, str]
model         = type_[BaseModel]
modelnone     = optional[type_[BaseModel]]
module_       = ModuleType
noreturn      = noreturn
path_         = Path
pathlist      = list_[path_]
set_          = set_
stranydict    = dict_[str, any_]
strcalldict   = dict_[str, callable_]
strdict       = stranydict
strbytes      = union_[str_, bytes]
strbooldict   = dict_[str, bool]
strcalldict   = dict_[str, callable_]
strdictdict   = dict_[str, anydict]
strdictlist   = list_[stranydict]
strdictnone   = union_[stranydict, None]
strint        = union_[str_, int]
strintbool    = union_[str_, int, bool]
strintdict    = dict_[str, int]
strintnone    = union_[strnone, intnone]
strlist       = list_[str]
strlistdict   = dict_[str, anylist]
strlistempty  = list_[strnone]
strlistnone   = optional[list_[str_]]
strordict     = union_[str, anydict]
strordictnone = union_[strnone, anydictnone]
strorfloat    = union_[str, float]
stroriter     = union_[str, anylist, anytuple]
strorlist     = listorstr
strorlistnone = optional[listorstr]
strset        = set_[str]
strsetdict    = dict_[str, anyset]
strstrdict    = dict_[str, str]
strtuple      = tuple_[str, ...]
textio_       = textio_
textionone    = textio_
tuple_        = tuple_
tuplist       = union_[anylist, anytuple]
tupnone       = optional[anytuple]
type_         = type_
typealias_    = typealias_
typevar_      = typevar_
union_        = union_

# ################################################################################################################################
# ################################################################################################################################

def instance_from_dict(class_:'any_', data:'anydict') -> 'any_':
    instance = class_()
    for key, value in data.items():
        setattr(instance, key, value)
    return instance

# ################################################################################################################################

def is_union(elem:'any_') -> 'bool':
    origin = getattr(elem, '__origin__', None) # type: any_
    return origin and getattr(origin, '_name', '') == 'Union'

# ################################################################################################################################

def extract_from_union(elem:'any_') -> 'anytuple':
    field_type_args = elem.__args__ # type: anylist
    field_type = field_type_args[0]
    union_with = field_type_args[1]

    return field_type_args, field_type, union_with

# ################################################################################################################################

def list_field() -> 'callable_[anylist]': # type: ignore
    return field(default_factory=list) # noqa: F405

# ################################################################################################################################

def dict_field() -> 'callable_[anydict]': # type: ignore
    return field(default_factory=dict) # noqa: F405

# ################################################################################################################################
# ################################################################################################################################
