from typing import Any, TYPE_CHECKING

from logging import basicConfig, getLogger, WARN
from traceback import format_exc
from unittest import TestCase
from zato.common.test.config import TestConfig
from sh import RunningCommand
from zato.common.typing_ import any_
from zato.common.util.cli import get_zato_sh_command


class BaseEnmasseTestCase(TestCase):
    def _warn_on_error(self: Any, stdout: any_, stderr: any_) -> None: ...
    def _assert_command_line_result(self: Any, out: RunningCommand) -> None: ...
    def invoke_enmasse(self: Any, config_path: str, require_ok: bool = ..., missing_wait_time: int = ..., is_import: bool = ..., is_export: bool = ..., include_type: str = ...) -> RunningCommand: ...
