from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
import re as stdlib_re
from datetime import datetime
from logging import getLogger
from operator import itemgetter
from uuid import uuid4
from regex import compile as re_compile
from zato.bunch import bunchify
from zato.common.api import HTTP_SOAP, MISC, TRACE1

http_any_internal = HTTP_SOAP.ACCEPT.ANY_INTERNAL

class Matcher:
    __repr__: Any
    ignore_http_methods: set
    group_names: Any
    pattern: Any
    matcher: Any
    is_static: Any
    _brace_pattern: re_compile
    _elem_re_template: Any
    def __init__(self: Any, pattern: Any, match_slash: Any = ...) -> None: ...
    def __str__(self: Any) -> None: ...
    def _set_up_matcher(self: Any, pattern: Any) -> None: ...
    def match(self: Any, value: Any) -> None: ...

class PyURLData:
    channel_data: Any
    url_path_cache: Any
    url_target_cache: Any
    has_trace1: logger.isEnabledFor
    def __init__(self: Any, channel_data: Any = ...) -> None: ...
    def _remove_from_cache(self: Any, match_target: Any) -> None: ...
    def match(self: Any, url_path: Any, http_method: Any, http_accept: Any, sep: Any = ..., _bunchify: Any = ..., _log_trace1: Any = ..., _trace1: Any = ...) -> None: ...
