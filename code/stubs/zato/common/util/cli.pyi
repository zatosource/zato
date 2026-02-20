from typing import Any, TYPE_CHECKING

from json import dumps
import select
import sys
from sh import RunningCommand
from zato.cli import ServerAwareCommand
from zato.common.typing_ import any_, anydict, anylist, stranydict
import sh
from sh import CommandNotFound
from zato.common.test.config import TestConfig


class CommandName:
    Default: Any
    PackageFullPath: Any

def get_zato_sh_command(command_name: str = ...) -> RunningCommand: ...

def read_stdin_data(strip: Any = ...) -> None: ...

class CommandLineInvoker:
    check_stdout: Any
    check_exit_code: Any
    expected_stdout: Any
    server_location: Any
    def __init__(self: Any, expected_stdout: Any = ..., check_stdout: Any = ..., check_exit_code: Any = ..., server_location: Any = ...) -> None: ...
    def _assert_command_line_result(self: Any, out: RunningCommand) -> None: ...
    def invoke_cli(self: Any, cli_params: anylist, command_name: str = ...) -> RunningCommand: ...

class CommandLineServiceInvoker(CommandLineInvoker):
    def invoke(self: Any, service: str, request: anydict) -> any_: ...
    def invoke_and_test(self: Any, service: str) -> any_: ...

class _AuthManager:
    command: Any
    is_active: Any
    create_service: str
    change_password_service: str
    name: Any
    password: Any
    def __init__(self: Any, command: ServerAwareCommand, name: str, is_active: bool, password: str) -> None: ...
    def _create(self: Any, create_request: stranydict, needs_stdout: bool = ...) -> stranydict: ...
    def _change_password(self: Any, name: str, password: str, needs_stdout: bool = ...) -> stranydict: ...

class BasicAuthManager(_AuthManager):
    create_service: Any
    change_password_service: Any
    username: Any
    realm: Any
    def __init__(self: Any, command: ServerAwareCommand, name: str, is_active: bool, username: str, realm: str, password: str) -> None: ...
    def create(self: Any, needs_stdout: bool = ...) -> stranydict: ...
    def change_password(self: Any, needs_stdout: bool = ...) -> stranydict: ...

class APIKeyManager(_AuthManager):
    create_service: Any
    change_password_service: Any
    header: Any
    key: Any
    def __init__(self: Any, command: ServerAwareCommand, name: str, is_active: bool, header: str, key: str) -> None: ...
    def create(self: Any, needs_stdout: bool = ...) -> stranydict: ...
