from typing import Any, TYPE_CHECKING

from zato.cli import ServerAwareCommand
from zato.common.api import CommonObject
from argparse import Namespace
import sys


class DeleteCommon(ServerAwareCommand):
    object_type: Any
    opts: Any
    def execute(self: Any, args: Namespace) -> None: ...
