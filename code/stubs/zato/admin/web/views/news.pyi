from typing import Any, TYPE_CHECKING

import configparser
from io import StringIO
from logging import getLogger
import requests
from django.http import JsonResponse
from zato.admin.web.views import method_allowed


def get_news(req: Any) -> None: ...
