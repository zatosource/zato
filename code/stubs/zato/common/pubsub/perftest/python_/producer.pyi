from typing import Any

import os
from json import dumps
from logging import getLogger
import requests
from requests.exceptions import ConnectionError
from zato.common.util.api import utcnow
from zato.common.pubsub.perftest.python_.client import Client
from zato.common.typing_ import anydict, intnone
from zato.common.pubsub.perftest.python_.progress_tracker import ProgressTracker

class Producer(Client):
    def __init__(self: Any, progress_tracker: ProgressTracker, reqs_per_producer: int = ..., producer_id: int = ..., reqs_per_second: float = ..., topic_spec: str = ..., burst_multiplier: int = ..., burst_duration: int = ..., burst_interval: int = ..., cpu_num: intnone = ..., use_new_requests: bool = ...) -> None: ...
    def _get_config(self: Any) -> anydict: ...
    def _create_payload(self: Any, topic_name: str) -> anydict: ...
    def _publish_message(self: Any, url: str, payload: anydict, headers: anydict, auth: tuple) -> None: ...
    def start(self: Any) -> None: ...
