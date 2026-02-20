from typing import Any, TYPE_CHECKING

from logging import getLogger
from traceback import format_exc
from django.http import StreamingHttpResponse
from zato.admin.web.views import method_allowed
from zato.admin.web.views.ai.common import get_api_key, is_valid_provider
from zato.admin.web.views.ai.llm.core import get_llm_client
from zato.common.ai.models import get_all_models
from zato.common.json_internal import dumps, loads
from zato.common.typing_ import any_, generator_
from django.http import JsonResponse
from zato.admin.web.views.ai.browser_tools import submit_browser_tool_result
from curl_cffi import requests as curl_requests
from html.parser import HTMLParser
from zato.admin.web.views.ai.llm.execution import clear_session_state


def _get_provider_for_model(model_id: str) -> str | None: ...

def _format_sse_event(event_type: str, data: dict) -> str: ...

def _stream_response(model_id: str, messages: list, zato_client: any_ = ..., cluster_id: int = ..., cluster: any_ = ..., session_id: str = ...) -> generator_: ...

def invoke(req: Any) -> StreamingHttpResponse: ...

def browser_tool_result(req: Any) -> None: ...

def fetch_page(req: Any) -> None: ...

def search_internet(req: Any) -> None: ...
