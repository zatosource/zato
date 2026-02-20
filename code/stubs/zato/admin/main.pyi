from typing import Any, TYPE_CHECKING

import logging
import os
import django
from django.core.management import call_command, execute_from_command_line
from zato.admin.zato_settings import update_globals
from zato.common.json_internal import loads
from zato.common.repo import RepoManager
from zato.common.util.api import store_pidfile
from zato.common.util.open_ import open_r
import cloghandler
import pymysql
import sys
from json import loads
from zato.common.util.api import parse_cmd_line_options
from zato.common.util.env import populate_environment_from_file


def update_password(base_dir: str) -> None: ...

def main() -> None: ...
