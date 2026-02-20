from typing import Any, TYPE_CHECKING

import os
import subprocess
import sys
import tempfile
from logging import getLogger
from traceback import format_exc
from uuid import uuid4
import yaml
import requests as requests_lib
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from zato.admin.web.views import method_allowed
from zato.common.json_internal import dumps, loads
from zato.common.util import openapi_ as openapi_module


def json_response(data: Any, success: Any = ...) -> None: ...

def parse(req: Any) -> None: ...

def fetch_url(req: Any) -> None: ...

def import_objects(req: Any) -> None: ...

def build_enmasse_config(items: Any) -> None: ...

def map_auth_to_security_type(auth: Any) -> None: ...
