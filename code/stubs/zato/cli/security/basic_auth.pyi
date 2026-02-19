from typing import Any

import sys
from uuid import uuid4
from zato.cli import ServerAwareCommand
from zato.common.util.api import fs_safe_now
from argparse import Namespace
from os import environ
from zato.common.util.cli import BasicAuthManager

class CreateDefinition(ServerAwareCommand):
    allow_empty_secrets: Any
    opts: Any
    def execute(self: Any, args: Namespace) -> None: ...

class ChangePassword(ServerAwareCommand):
    allow_empty_secrets: Any
    opts: Any
    def execute(self: Any, args: Namespace) -> None: ...

class DeleteDefinition(ServerAwareCommand):
    opts: Any
    def execute(self: Any, args: Namespace) -> None: ...
