from typing import Any, TYPE_CHECKING

from threading import Lock
from colorama import Fore, Style
from zato.common.util.api import utcnow
from datetime import timedelta


class ProgressTracker:
    total_producers: Any
    total_messages: Any
    completed_messages: Any
    failed_messages: Any
    start_time: utcnow
    lock: Lock
    message_timestamps: Any
    last_trim_time: utcnow
    def __init__(self: Any, total_producers: int, total_messages: int) -> None: ...
    def update_progress(self: Any, success: bool = ..., count: int = ...) -> None: ...
    def _display_progress(self: Any) -> None: ...
    def finish(self: Any) -> None: ...
