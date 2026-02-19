from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from zato.cli import ManageCommand
from zato.common.util.open_ import open_r
import os
import sys
import signal
from zato.common.util.updates import setup_update_file_logger

class Stop(ManageCommand):
    def signal(self: Any, component_name: Any, signal_name: Any, signal_code: Any, pidfile: Any = ..., component_dir: Any = ..., ignore_missing: Any = ..., needs_logging: Any = ...) -> None: ...
    def _on_server(self: Any, *ignored: Any) -> None: ...
    def _on_web_admin(self: Any, *ignored: Any) -> None: ...
    def _on_scheduler(self: Any, *ignored: Any) -> None: ...
