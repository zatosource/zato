from typing import Any


class HaltServer(BaseException):
    reason: Any
    exit_status: Any
    def __init__(self: Any, reason: Any, exit_status: Any = ...) -> None: ...
    def __str__(self: Any) -> None: ...

class ConfigError(Exception):
    ...

class AppImportError(Exception):
    ...
