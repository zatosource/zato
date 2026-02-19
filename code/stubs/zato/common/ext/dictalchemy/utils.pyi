from typing import Any

from __future__ import absolute_import, division
import copy
from sqlalchemy import inspect
from sqlalchemy.ext.associationproxy import _AssociationList
from sqlalchemy.orm.dynamic import AppenderMixin
from sqlalchemy.orm.query import Query
from zato.common.ext.dictalchemy import constants
from zato.common.ext.dictalchemy import errors

def arg_to_dict(arg: Any) -> None: ...

def asdict(model: Any, exclude: Any = ..., exclude_underscore: Any = ..., exclude_pk: Any = ..., follow: Any = ..., include: Any = ..., only: Any = ..., method: Any = ..., **kwargs: Any) -> None: ...

def fromdict(model: Any, data: Any, exclude: Any = ..., exclude_underscore: Any = ..., allow_pk: Any = ..., follow: Any = ..., include: Any = ..., only: Any = ...) -> None: ...

def iter(model: Any) -> None: ...

def make_class_dictable(cls: Any, exclude: Any = ..., exclude_underscore: Any = ..., fromdict_allow_pk: Any = ..., include: Any = ..., asdict_include: Any = ..., fromdict_include: Any = ...) -> None: ...
