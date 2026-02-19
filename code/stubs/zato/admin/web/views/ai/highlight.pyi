from typing import Any

from http.client import BAD_REQUEST
from logging import getLogger
from django.http import JsonResponse
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound
from zato.admin.web.views import method_allowed
from zato.common.json_internal import loads

def highlight_code(req: Any) -> JsonResponse: ...

def get_pygments_css(req: Any) -> JsonResponse: ...
