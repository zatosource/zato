from typing import Any, TYPE_CHECKING

from logging import getLogger
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from zato.common.json_internal import dumps


def json_response(data: Any, success: Any = ...) -> None: ...

def restart_component(req: Any, updater: Any, component_name: Any, component_path: Any, port: Any = ...) -> None: ...
