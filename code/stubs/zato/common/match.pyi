from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
import logging
from globre import match as globre_match
from zato.common.api import FALSE_TRUE, TRUE_FALSE
from zato.common.util.api import as_bool

class Matcher:
    config: Any
    items: Any
    order1: Any
    order2: Any
    is_allowed_cache: Any
    special_case: Any
    def __init__(self: Any) -> None: ...
    def read_config(self: Any, config: Any) -> None: ...
    def is_allowed(self: Any, value: Any) -> None: ...
