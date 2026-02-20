from typing import Any, TYPE_CHECKING

from copy import deepcopy
from zato.cli import common_odb_opts, ZatoCommand
from zato.common.const import ServiceConst
from zato.common.util.open_ import open_r, open_w
import os
import pymysql
import json
from random import getrandbits
from uuid import uuid4
from django.core.management import call_command
from zato.common.py23_.past.builtins import unicode
from zato.admin.zato_settings import update_globals
from zato.cli import is_arg_given
from zato.common.crypto.api import WebAdminCryptoManager
from zato.common.crypto.const import well_known_data
from zato.common.defaults import web_admin_host, web_admin_port
from zato.common.util.logging_ import get_logging_conf_contents
import platform
import django
from django.contrib.auth.models import User
from django.core.management.base import CommandError
from django.db import connection
from django.db.utils import IntegrityError


class Create(ZatoCommand):
    needs_empty_dir: Any
    opts: Any
    target_dir: os.path.abspath
    def __init__(self: Any, args: Any) -> None: ...
    def allow_empty_secrets(self: Any) -> None: ...
    def execute(self: Any, args: Any, show_output: Any = ..., admin_password: Any = ..., needs_admin_created_flag: Any = ...) -> None: ...
