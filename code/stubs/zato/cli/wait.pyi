from typing import Any, TYPE_CHECKING

from zato.cli import ZatoCommand
from argparse import Namespace
from zato.common.typing_ import intnone
from os import environ
import sys
from zato.common.util.api import get_client_from_server_conf
from zato.common.util.tcp import wait_for_zato


class Wait(ZatoCommand):
    opts: Any
    def execute(self: Any, args: Namespace, needs_sys_exit: bool = ...) -> intnone: ...
