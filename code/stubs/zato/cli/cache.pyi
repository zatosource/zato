from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from zato.cli import ManageCommand
from argparse import Namespace
from zato.client import JSONResponse
import sys
from zato.common.api import NotGiven
from zato.common.util.cache import Client as CacheClient, CommandConfig

class CacheCommand(ManageCommand):
    opts: Any
    def _on_server(self: Any, args: Any, _modifiers: Any = ...) -> None: ...

class CacheGet(CacheCommand):
    opts: Any

class CacheSet(CacheCommand):
    opts: Any

class CacheDelete(CacheCommand):
    opts: Any
