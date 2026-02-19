from typing import Any

from http.client import OK
from logging import getLogger
from bunch import Bunch
from django.urls import resolve
from zato.admin.settings import ADMIN_INVOKE_NAME, ADMIN_INVOKE_PASSWORD, ADMIN_INVOKE_PATH, SASession, settings_db
from zato.admin.web.forms import SearchForm
from zato.admin.web.models import ClusterColorMarker
from zato.admin.web.util import get_user_profile
from zato.client import AnyServiceInvoker
from zato.common.json_internal import loads
from zato.common.odb.model import Cluster
from zato.common.version import get_version
from zato.common.typing_ import anydict

class HeadersEnrichedException(Exception):
    headers: anydict

class Client(AnyServiceInvoker):
    def __init__(self: Any, req: Any, *args: Any, **kwargs: Any) -> None: ...
    def invoke(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def invoke_async(self: Any, *args: Any, **kwargs: Any) -> None: ...

class ZatoMiddleware:
    def __init__(self: Any, get_response: Any) -> None: ...
    def __call__(self: Any, req: Any) -> None: ...
    def process_request(self: Any, req: Any) -> None: ...
    def process_response(self: Any, req: Any, resp: Any) -> None: ...
    def process_template_response(self: Any, req: Any, resp: Any) -> None: ...
