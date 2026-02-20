from typing import Any, TYPE_CHECKING

import sys
from zato.common.py23_.past.utils import with_metaclass

_builtin_dict = dict
ver = sys.version_info[Any]

class BaseOldDict(type):
    def __instancecheck__(cls: Any, instance: Any) -> None: ...

class olddict(with_metaclass):
    iterkeys: Any
    viewkeys: Any
    itervalues: Any
    viewvalues: Any
    iteritems: Any
    viewitems: Any
    def keys(self: Any) -> None: ...
    def values(self: Any) -> None: ...
    def items(self: Any) -> None: ...
    def has_key(self: Any, k: Any) -> None: ...
    def __native__(self: Any) -> None: ...
