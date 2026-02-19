from typing import Any

import logging
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
import pyotp
from zato.common.py23_.past.builtins import unicode
from zato.admin import zato_settings
from zato.admin.web.forms.account import BasicSettingsForm
from zato.admin.web.models import ClusterColorMarker
from zato.admin.web.util import set_user_profile_totp_key
from zato.admin.web.views import method_allowed
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import dumps, loads

def set_initial_opaque_attrs(username: Any, initial: Any, opaque_attrs: Any) -> None: ...

def settings_basic(req: Any) -> None: ...

def settings_basic_save(req: Any) -> None: ...

def generate_totp_key(req: Any) -> None: ...
