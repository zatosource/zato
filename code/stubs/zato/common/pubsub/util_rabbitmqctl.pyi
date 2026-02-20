from typing import Any, TYPE_CHECKING

import json
import logging
import os
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from logging import getLogger
from zato.common.util.api import as_bool


def setup_logging() -> None: ...

class RabbitMQCtlHandler(BaseHTTPRequestHandler):
    def do_POST(self: Any) -> None: ...
    def log_message(self: Any, format: Any, *args: Any) -> None: ...

def start_server() -> None: ...
