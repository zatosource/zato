from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
from zato.common.const import SECRETS
from zato.common.util.api import parse_cmd_line_options


def resolve_secret_key(secret_key: Any, _url_prefix: Any = ...) -> None: ...
