from typing import Any, TYPE_CHECKING

from logging import getLogger
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
import pyotp
from zato.admin.settings import LOGIN_REDIRECT_URL
from zato.admin import zato_settings
from zato.admin.web.forms.main import AuthenticationForm
from zato.admin.web.util import get_user_profile
from zato.admin.web.views import method_allowed
from zato.common.crypto.api import CryptoManager


def index_redirect(req: Any) -> None: ...

def index(req: Any) -> None: ...

def get_login_response(req: Any, needs_post_form_data: Any, has_errors: Any) -> None: ...

def login(req: Any) -> None: ...

def logout(req: Any) -> None: ...
