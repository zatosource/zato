from typing import Any, TYPE_CHECKING

import mimetypes
import posixpath
from logging import getLogger
from pathlib import Path
from django.http import FileResponse, Http404, HttpResponseNotModified
from django.template.response import TemplateResponse
from django.utils._os import safe_join
from django.utils.http import http_date, parse_http_date
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import loads
from zato.common.util.platform_ import is_windows
from zato.admin.web.models import UserProfile


def get_template_response(req: Any, template_name: Any, return_data: Any) -> None: ...

def get_user_profile(user: Any, needs_logging: Any = ...) -> None: ...

def set_user_profile_totp_key(user_profile: Any, zato_secret_key: Any, totp_key: Any, totp_key_label: Any = ..., opaque_attrs: Any = ...) -> None: ...

def static_serve(request: Any, path: Any, document_root: Any = ..., show_indexes: Any = ...) -> None: ...

def was_modified_since(header: Any = ..., mtime: Any = ...) -> None: ...

def get_pubsub_security_definitions(request: Any, form_type: Any = ..., context: Any = ...) -> None: ...

def get_pubsub_security_choices(request: Any, form_type: Any = ..., context: Any = ...) -> None: ...

def get_service_list(request: Any) -> None: ...
