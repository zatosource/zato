from typing import Any

import os
import json
import time
from logging import getLogger
from traceback import format_exc
from requests.exceptions import ConnectionError
from prometheus_client import Counter, Histogram, push_to_gateway, CollectorRegistry
from zato.common.pubsub.perftest.python_.client import Client
from zato.common.util.api import utcnow
from zato.common.typing_ import anydict, intnone
from zato.common.pubsub.perftest.python_.progress_tracker import ProgressTracker

class Consumer(Client):
    def __init__(self: Any, progress_tracker: ProgressTracker, consumer_id: int = ..., pull_interval: float = ..., max_messages: int = ..., cpu_num: intnone = ..., use_new_requests: bool = ...) -> None: ...
    def _get_config(self: Any) -> anydict: ...
    def _consume_messages(self: Any, base_url: str, headers: anydict, auth: tuple, max_messages: int) -> None: ...
    def start(self: Any) -> None: ...
