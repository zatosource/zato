from typing import Any, TYPE_CHECKING

import random
import time
from datetime import datetime, timedelta
from zato.common.util.api import utcnow


def get_remaining_time(start_time: datetime, max_seconds: int) -> timedelta: ...

def get_sleep_time(start_time: datetime, max_seconds: int, attempt_number: int, jitter_range: float = ...) -> float: ...

def simulate_sleep_times() -> None: ...
