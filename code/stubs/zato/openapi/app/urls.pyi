from typing import Any, TYPE_CHECKING

from django.conf import settings
from django.urls import path
from zato.openapi.app.views import swagger_view, serve_openapi
from django.http import FileResponse
import os


def serve_static_with_mime(request: Any, file_path: Any, mime_type: Any) -> None: ...
