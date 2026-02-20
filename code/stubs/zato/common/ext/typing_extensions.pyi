from typing import Any, TYPE_CHECKING

import abc
import collections
import collections.abc
import operator
import sys
import typing
from typing import GenericMeta, _type_vars
from _collections_abc import _check_methods as _check_methods_in_mro
from typing import _collect_type_vars
from typing import _next_in_mro, _type_check
from typing import _BaseGenericAlias
from typing import GenericAlias
import warnings

ClassVar = typing.ClassVar
_overload_dummy = typing._overload_dummy
overload = typing.overload
Type = typing.Type
Awaitable = typing.Awaitable
Coroutine = typing.Coroutine
AsyncIterable = typing.AsyncIterable
AsyncIterator = typing.AsyncIterator
ContextManager = typing.ContextManager
DefaultDict = typing.DefaultDict
NewType = typing.NewType
Text = typing.Text
TYPE_CHECKING = typing.TYPE_CHECKING
runtime = runtime_checkable

def _no_slots_copy(dct: Any) -> None: ...

def _check_generic(cls: Any, parameters: Any) -> None: ...

def IntVar(name: Any) -> None: ...

class _ExtensionsGenericMeta(GenericMeta):
    def __subclasscheck__(self: Any, subclass: Any) -> None: ...

def _gorg(cls: Any) -> None: ...

def _get_protocol_attrs(cls: Any) -> None: ...

def _is_callable_members_only(cls: Any) -> None: ...

def _concatenate_getitem(self: Any, parameters: Any) -> None: ...
