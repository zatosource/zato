from typing import Any, TYPE_CHECKING

import logging
import os
import socket
from ddtrace import patch
from ddtrace.trace import tracer


class DatadogDemo:
    host_name: socket.gethostname
    def __init__(self: Any) -> None: ...
    def setup(self: Any) -> None: ...
    def run(self: Any) -> None: ...
