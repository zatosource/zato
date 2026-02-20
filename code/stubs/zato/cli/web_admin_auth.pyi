from typing import Any

import os
from zato.cli import common_totp_opts, ManageCommand
from zato.common.const import ServiceConst
from zato.common.util.open_ import open_r, open_w
import pymysql
from zato.admin.zato_settings import update_globals
from zato.common.json_internal import loads
import django
import sys
from traceback import format_exc
from django.contrib.auth.management.commands.createsuperuser import Command
from django.contrib.auth.management.commands.changepassword import Command
from zato.admin.web.util import set_user_profile_totp_key
from zato.admin.web.models import User
from zato.admin.web.util import get_user_profile
from zato.admin.zato_settings import zato_secret_key
from zato.cli.util import get_totp_info_from_args
from zato.common.json_internal import dumps
from zato.common.crypto.api import WebAdminCryptoManager
from zato.common.py23_.past.builtins import unicode
from django.core.validators import EmailValidator
from django.core import exceptions

class _WebAdminAuthCommand(ManageCommand):
    def _prepare(self: Any, args: Any) -> None: ...
    def _ok(self: Any, args: Any) -> None: ...

class CreateUser(_WebAdminAuthCommand):
    opts: Any
    is_interactive: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def is_password_required(self: Any) -> None: ...
    def before_execute(self: Any, args: Any) -> None: ...
    def execute(self: Any, args: Any, needs_sys_exit: Any = ...) -> None: ...

class UpdatePassword(_WebAdminAuthCommand):
    opts: Any
    def before_execute(self: Any, args: Any) -> None: ...
    def execute(self: Any, args: Any, called_from_wrapper: Any = ...) -> None: ...

class ResetTOTPKey(_WebAdminAuthCommand):
    opts: Any
    def before_execute(self: Any, args: Any) -> None: ...
    def execute(self: Any, args: Any) -> None: ...

class SetAdminInvokePassword(_WebAdminAuthCommand):
    opts: Any
    def execute(self: Any, args: Any) -> None: ...
