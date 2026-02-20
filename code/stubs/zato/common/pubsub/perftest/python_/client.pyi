from typing import Any, TYPE_CHECKING

import os
import requests
from zato.common.typing_ import anydict, intnone
from zato.common.pubsub.perftest.python_.progress_tracker import ProgressTracker


class Client:
    client_id: Any
    reqs_per_second: Any
    max_topics: Any
    progress_tracker: Any
    cpu_num: Any
    use_new_requests: Any
    session: requests.Session
    def __init__(self: Any, progress_tracker: ProgressTracker, client_id: int = ..., reqs_per_second: float = ..., max_topics: int = ..., cpu_num: intnone = ..., use_new_requests: bool = ...) -> None: ...
    def _before_start(self: Any) -> None: ...
    def _get_config(self: Any) -> anydict: ...
    def start(self: Any) -> None: ...
