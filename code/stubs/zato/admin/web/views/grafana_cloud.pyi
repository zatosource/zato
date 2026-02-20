from typing import Any, TYPE_CHECKING

import os
from logging import getLogger
from django.http import HttpResponse
from django.template.response import TemplateResponse
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.config import grafana_cloud_page_config
from zato.common.json_internal import dumps
from zato.common.util.updates import Updater, UpdaterConfig
from django.http.response import HttpResponseServerError
import subprocess as _subprocess
import threading
import base64
import requests
from http import HTTPStatus
from traceback import format_exc
from zato.common.json_internal import loads
import getpass
import redis
import subprocess
import tempfile
from zato.admin.web.views.otelcol_config import template as otelcol_template
import time


def json_response(data: Any, success: Any = ...) -> None: ...

def restart_component(req: Any, component_name: Any, component_path: Any, port: Any = ...) -> None: ...

def restart_scheduler(req: Any) -> None: ...

def restart_server(req: Any) -> None: ...

def restart_proxy(req: Any) -> None: ...

def restart_dashboard(req: Any) -> None: ...

def test_connection(req: Any) -> None: ...

def toggle_enabled(req: Any) -> None: ...

def save_config(req: Any) -> None: ...

def index(req: Any) -> None: ...
