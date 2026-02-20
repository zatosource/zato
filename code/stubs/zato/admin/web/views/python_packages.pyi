from typing import Any, TYPE_CHECKING

import os
import re
import subprocess
import threading
from logging import getLogger
from traceback import format_exc
import requests
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from django.template.response import TemplateResponse
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.config import python_packages_page_config
from zato.common.json_internal import dumps, loads
from zato.common.util.updates import Updater, UpdaterConfig
import time


def json_response(data: Any, success: Any = ...) -> None: ...

def restart_component(req: Any, component_name: Any, component_path: Any, port: Any = ...) -> None: ...

def restart_scheduler(req: Any) -> None: ...

def restart_server(req: Any) -> None: ...

def restart_proxy(req: Any) -> None: ...

def restart_dashboard(req: Any) -> None: ...

def _is_pypi_package(requirement_line: Any) -> None: ...

def _extract_package_name(requirement_line: Any) -> None: ...

def test_packages(req: Any) -> None: ...

def save_config(req: Any) -> None: ...

def index(req: Any) -> None: ...
