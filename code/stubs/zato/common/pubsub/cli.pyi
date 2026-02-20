from typing import Any

import argparse
import logging
import os
import sys
import threading
import time
from dataclasses import dataclass
from json import dumps
from logging import getLogger
from traceback import format_exc
from gunicorn.app.base import BaseApplication
from gunicorn.workers.sync import SyncWorker
from gunicorn import util
from prometheus_client import Histogram
from zato.common.api import PubSub
from zato.common.pubsub.server.rest_publish import PubSubRESTServerPublish
from zato.common.pubsub.server.rest_pull import PubSubRESTServerPull
from zato.common.pubsub.util import get_broker_config, cleanup_broker_impl
from zato.common.pubsub.util_cli import list_connections as list_connections_cli
from zato.common.util.api import as_bool, new_cid_cli
from zato.common.typing_ import anydictnone, dictnone
from zato.common.pubsub.server.rest_base import PubSubRESTServer
from prometheus_client import REGISTRY
from zato.common.pubsub.cli_enmasse import run_enmasse_command

class TimingWorker(SyncWorker):
    _socket_times: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def accept(self: Any, listener: Any) -> None: ...
    def handle_request(self: Any, listener: Any, req: Any, client: Any, addr: Any) -> None: ...

class GreenletFormatter(logging.Formatter):
    def format(self: Any, record: Any) -> None: ...

class GunicornApplication(BaseApplication):
    options: Any
    original_app: Any
    application: Any
    def __init__(self: Any, app: PubSubRESTServer, options: dictnone = ...) -> None: ...
    def load_config(self: Any) -> None: ...
    def load(self: Any) -> None: ...
    def on_post_fork(self: Any, server: Any, worker: Any) -> None: ...

class OperationResult:
    is_ok: bool
    message: str
    details: anydictnone

def get_parser() -> argparse.ArgumentParser: ...

def start_server(args: argparse.Namespace) -> OperationResult: ...

def cleanup_broker(args: argparse.Namespace) -> OperationResult: ...

def list_connections(args: argparse.Namespace) -> OperationResult: ...

def main() -> int: ...
