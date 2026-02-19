from typing import Any

from http.client import BAD_REQUEST
from logging import getLogger
from django.http import HttpResponse
from zato.admin.web.views import method_allowed
from zato.admin.web.views.ai.common import delete_api_key, get_all_api_key_status, is_valid_provider, set_api_key
from zato.common.ai.models import get_all_models
from zato.common.json_internal import dumps, loads

def get_keys(req: Any) -> HttpResponse: ...

def save_key(req: Any) -> HttpResponse: ...

def delete_key(req: Any) -> HttpResponse: ...

def get_models(req: Any) -> HttpResponse: ...
