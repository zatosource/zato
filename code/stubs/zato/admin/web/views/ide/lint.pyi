from typing import Any

import json
import subprocess
import tempfile
from logging import getLogger
from django.http import JsonResponse
from zato.admin.web.views import method_allowed
from zato.common.json_internal import loads
from django.http import HttpRequest
import os

def lint_python(req: HttpRequest) -> JsonResponse: ...
