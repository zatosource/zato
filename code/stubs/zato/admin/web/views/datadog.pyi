from typing import Any, TYPE_CHECKING

import os
import socket
import subprocess
import threading
import time
from logging import getLogger
from traceback import format_exc
import redis
import requests
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from django.template.response import TemplateResponse
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.config import datadog_page_config
from zato.common.json_internal import dumps, loads
from zato.common.util.updates import Updater, UpdaterConfig


def json_response(data: Any, success: Any = ...) -> None: ...

def restart_component(req: Any, component_name: Any, component_path: Any, port: Any = ...) -> None: ...

def restart_scheduler(req: Any) -> None: ...

def restart_server(req: Any) -> None: ...

def restart_proxy(req: Any) -> None: ...

def restart_dashboard(req: Any) -> None: ...

def _test_agent_connection(address: Any, label: Any, errors: Any, use_udp: Any = ...) -> None: ...

def test_connection(req: Any) -> None: ...

def toggle_enabled(req: Any) -> None: ...

def save_config(req: Any) -> None: ...

def index(req: Any) -> None: ...
