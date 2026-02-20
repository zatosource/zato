from typing import Any, TYPE_CHECKING

import random
import time
from zato.common.monitoring.api import create_context, get_metrics_data, incr_global, push_global
import argparse


class PrometheusTestServer:
    host: Any
    port: Any
    server: Any
    running: Any
    def __init__(self: Any, host: str = ..., port: int = ...) -> None: ...
    def wsgi_app(self: Any, environ: Any, start_response: Any) -> None: ...
    def _generate_demo_data(self: Any) -> None: ...
    def _background_metrics_generator(self: Any) -> None: ...
    def start(self: Any) -> None: ...

def main() -> None: ...
