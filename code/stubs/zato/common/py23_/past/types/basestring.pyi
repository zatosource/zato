from typing import Any, TYPE_CHECKING

import sys
from zato.common.py23_.past.utils import with_metaclass, PY2

ver = sys.version_info[Any]

class BaseBaseString(type):
    def __instancecheck__(cls: Any, instance: Any) -> None: ...
    def __subclasshook__(cls: Any, thing: Any) -> None: ...

class basestring(with_metaclass):
    ...
