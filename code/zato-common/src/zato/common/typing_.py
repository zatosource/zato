# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# stdlib
from datetime import datetime
from typing import           \
    Any as any_,             \
    BinaryIO as binaryio_,   \
    Callable as callable_,   \
    cast as cast_,           \
    Dict as dict_,           \
    Generator as generator_, \
    Iterator as iterator_,   \
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

# dacite
from dacite import from_dict

# typing-extensions
from typing_extensions import \
    TypeAlias as typealias_

# stdlib
from dataclasses import * # noqa: F401

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

anydict      = dict_[any_, any_]
anydictnone  = optional[anydict]
anylist      = list_[any_]
anylistnone  = optional[anylist]
anyset       = set_[any_]
anytuple     = tuple_[any_, ...]
binaryio_    = binaryio_
boolnone     = optional[bool]
callable_    = callable_[..., any_]
callnone     = optional[callable_]
cast_        = cast_
commondict   = dict_[str, union_[int, str_, bool, float, anydict, anylist, None]]
dictlist     = list_[anydict]
dictnone     = optional[anydict]
dtnone       = optional[datetime]
floatnone    = optional[float]
generator_   = generator_
intanydict   = dict_[int, any_]
intdict      = dict_[int, int]
intdictdict  = dict_[int, anydict]
intlist      = list_[int]
intnone      = optional[int]
intlistempty = list_[intnone]
intlistnone  = optional[list_[int]]
intset       = set_[int]
intsetdict   = dict_[int, anyset]
intstrdict   = dict_[int, str]
iterator_    = iterator_
noreturn     = noreturn
set_         = set_
stranydict   = dict_[str, any_]
strlistdict  = dict_[str, anylist]
strdictdict  = dict_[str, anydict]
strint       = union_[str_, int]
strintbool   = union_[str_, int, bool]
strintdict   = dict_[str, int]
strintnone   = union_[optional[str_], optional[int]]
strlist      = list_[str]
strlistdict  = dict_[str, anylist]
strlistempty = list_[optional[str]]
strlistnone  = optional[list_[str]]
strnone      = optional[str]
strorlist    = union_[str, anylist]
strset       = set_[str]
strsetdict   = dict_[str, anyset]
strstrdict   = dict_[str, str]
strtuple     = tuple_[str, ...]
textio_      = textio_
tuple_       = tuple_
type_        = type_
typealias_   = typealias_
typevar_     = typevar_
union_       = union_

# ################################################################################################################################
# ################################################################################################################################

def instance_from_dict(class_:'any_', data:'dict') -> 'any_':
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

def list_field() -> 'callable_[anylist]':
    return field(default_factory=list) # noqa: F405

# ################################################################################################################################
# ################################################################################################################################
