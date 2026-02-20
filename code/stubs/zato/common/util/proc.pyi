from typing import Any, TYPE_CHECKING

import os
import sys
from logging import getLogger
from tempfile import mkstemp
from time import time, sleep
from sarge import run as sarge_run, shell_format
import platform
from zato.common.api import CLI_ARG_SEP
from zato.common.util.open_ import open_r
from zato.common.typing_ import any_, strdict, textio_


def get_executable() -> str: ...

class _StdErr:
    ignored: Any
    path: Any
    timeout: Any
    def __init__(self: Any, path: str, timeout: float) -> None: ...
    def wait_for_error(self: Any) -> None: ...
    def should_ignore(self: Any, err: str) -> bool: ...

def start_process(component_name: str, executable: str, run_in_fg: bool, cli_options: str | None, extra_cli_options: str = ..., on_keyboard_interrupt: any_ = ..., failed_to_start_err: int = ..., extra_options: strdict | None = ..., stderr_path: str | None = ..., stdin_data: str | None = ..., async_keyword: str = ..., env_vars: strdict | None = ...) -> int: ...

def start_python_process(component_name: str, run_in_fg: bool, py_path: str, program_dir: str, on_keyboard_interrupt: any_ = ..., failed_to_start_err: int = ..., extra_options: strdict | None = ..., stderr_path: str | None = ..., stdin_data: str | None = ..., env_vars: strdict | None = ...) -> int: ...
