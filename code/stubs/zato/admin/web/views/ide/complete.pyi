from typing import Any, TYPE_CHECKING

import json
import os
import subprocess
import sys
import tempfile
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR
from logging import getLogger
from traceback import format_exc
from django.http import JsonResponse
from zato.admin.web.views import method_allowed
from zato.common.api import IDE_Ignore_Modules
from zato.common.json_internal import loads
from django.http import HttpRequest


def build_lsp_message(content: Any) -> None: ...

def parse_lsp_response(output: Any) -> None: ...

def complete_python(req: HttpRequest) -> JsonResponse: ...
