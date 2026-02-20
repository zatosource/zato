from typing import Any, TYPE_CHECKING

import time
from logging import getLogger
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from zato.admin.web.views import method_allowed


def dashboard_create_page(req: Any) -> None: ...

def create_grafana_dashboard(req: Any) -> None: ...

def create_datadog_dashboard(req: Any) -> None: ...

def try_service_code(req: Any) -> None: ...
