from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from zato.cli import ManageCommand
from zato.common.api import INFO_FORMAT
import os
import yaml
from zato.common.component_info import format_info, get_info


class Info(ManageCommand):
    opts: Any
    _on_scheduler: Any
    _on_web_admin: Any
    def _on_server(self: Any, args: Any) -> None: ...
