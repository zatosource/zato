from typing import Any, TYPE_CHECKING

from logging import getLogger
from traceback import format_exc
from django.http import HttpResponse, StreamingHttpResponse
from zato.admin.web.views import method_allowed
from zato.common.json_internal import dumps
import redis
import time
import json


def toggle_streaming(req: Any) -> None: ...

def get_status(req: Any) -> None: ...

def log_stream(req: Any) -> None: ...
