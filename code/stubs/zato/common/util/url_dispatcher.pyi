from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from logging import getLogger
from zato.common.api import HTTP_SOAP, MISC

accept_any_http = HTTP_SOAP.ACCEPT.ANY
accept_any_internal = HTTP_SOAP.ACCEPT.ANY_INTERNAL
method_any_internal = HTTP_SOAP.METHOD.ANY_INTERNAL

def get_match_target(config: Any, sep: Any = ..., accept_any_http: Any = ..., accept_any_internal: Any = ..., method_any_internal: Any = ..., http_methods_allowed_re: Any = ...) -> None: ...
