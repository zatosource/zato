from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from json import load, loads
from ujson import dump, dumps
from json import dump, dumps

def handle_default(obj: Any) -> None: ...

def dumps(obj: Any, **kwargs: Any) -> None: ...
