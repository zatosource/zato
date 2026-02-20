from typing import Any, TYPE_CHECKING

import warnings
from dataclasses import dataclass
from datetime import datetime
from inspect import isclass
from logging import getLogger
from humanize import naturalsize
from zato.common.marshal_.api import Model
from zato.common.util.platform_ import is_windows
from zato.common.typing_ import cast_
from zato.common.util import new_cid
from zato.common.util.api import get_zato_command
from zato.common.util.time_ import utcnow
from pathlib import Path
from zato.common.typing_ import any_
from zato.server.base.parallel import ParallelServer
from zato.server.service import Service


class Config:
    UsePubSub: Any
    Timeout: Any
    Encoding: Any
    ReplaceChar: Any

class CommandResult(Model):
    cid: str
    command: str
    callback: any_
    stdin: str
    stdout: str
    stderr: str
    is_async: bool
    use_pubsub: bool
    is_ok: bool
    timeout: float
    exit_code: int
    len_stdout_bytes: int
    len_stderr_bytes: int
    len_stdout_human: str
    len_stderr_human: str
    encoding: str
    replace_char: str
    is_timeout: bool
    timeout_msg: str 
    start_time: datetime
    start_time_iso: str
    end_time: datetime
    end_time_iso: str
    total_time: str
    total_time_sec: float

class CommandsFacade:
    server: ParallelServer
    def init(self: Any, server: ParallelServer) -> None: ...
    def _append_time_details(self: Any, out: CommandResult) -> None: ...
    def _append_result_details(self: Any, out: CommandResult, result: CompletedProcess, encoding: str, replace_char: str) -> None: ...
    def _run(self: Any) -> CommandResult: ...
    def _run_callback(self: Any, cid: str, callback: any_, result: CommandResult, use_pubsub: bool) -> None: ...
    def invoke_async(self: Any, command: str) -> CommandResult: ...
    def invoke(self: Any, command: str) -> CommandResult: ...
    def run_zato_cli_sync(self: Any, command: str, callback: any_ = ...) -> CommandResult: ...
    def run_zato_cli_async(self: Any, command: str, callback: any_ = ...) -> CommandResult: ...
    def run_enmasse_sync_export(self: Any) -> CommandResult: ...
    def run_enmasse_sync_import(self: Any, file_path: str | Path, missing_wait_time: int = ...) -> CommandResult: ...
    def run_enmasse_async_import(self: Any, file_path: str | Path) -> CommandResult: ...
    def _on_enmasse_completed(self: Any, result: CommandResult) -> None: ...
