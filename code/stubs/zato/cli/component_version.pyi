from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from zato.cli import ZatoCommand
from zato.common.api import ZATO_INFO_FILE
from zato.common.util.open_ import open_r
import os
from zato.common.json_internal import load


class ComponentVersion(ZatoCommand):
    file_needed: Any
    def execute(self: Any, args: Any) -> None: ...
