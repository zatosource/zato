from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from traceback import format_exc
from zato.common.api import DATA_FORMAT
from zato.common.json_internal import dumps
from zato.server.service import Service


class Create(Service):
    def handle(self: Any) -> None: ...
