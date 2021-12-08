# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# stdlib
from typing import           \
    Any as any_,             \
    Dict as dict_,           \
    Generator as generator_, \
    NoReturn as noreturn,    \
    List as list_,           \
    Optional as optional,    \
    Tuple as tuple_,         \
    Set as set_,             \
    Union as union_

# dacite
from dacite import from_dict

# Be explicit about which import error we want to catch
try:
    import dataclasses # noqa: F401

# Python 3.6
except ImportError:
    from zato.common.ext.dataclasses import * # noqa: F401

# Python 3.6+
else:
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

def instance_from_dict(class_, data):
    # type: (object, dict) -> object
    instance = class_()
    for key, value in data.items():
        setattr(instance, key, value)
    return instance

# ################################################################################################################################
# ################################################################################################################################

anydict    = dict_[any_, any_]
anylist    = list_[any_]
anytuple   = tuple_[any_, ...]
dictlist   = list_[anydict]
generator_ = generator_
intnone    = optional[int]
noreturn   = noreturn
set_       = set_
strnone    = optional[str]
strlist    = list_[str]
strintdict = dict_[str, int]
intdict    = dict_[int, int]
strtuple   = tuple_[str]
tuple_     = tuple_
union_     = union_
