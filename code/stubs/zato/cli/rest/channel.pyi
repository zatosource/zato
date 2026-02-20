from typing import Any, TYPE_CHECKING

import sys
from uuid import uuid4
from zato.cli import ServerAwareCommand
from zato.common.api import CONNECTION, ZATO_NONE
from zato.common.util.api import fs_safe_now
from argparse import Namespace
from zato.common.typing_ import anytuple, stranydict
from os import environ
from zato.common.util.cli import APIKeyManager, BasicAuthManager


class Config:
    ServiceName: Any
    MaxBytesRequests: Any
    MaxBytesResponses: Any

class SecurityAwareCommand(ServerAwareCommand):
    def _extract_credentials(self: Any, name: str, credentials: str, needs_header: bool) -> anytuple: ...
    def _get_security_id(self: Any) -> stranydict: ...

class CreateChannel(SecurityAwareCommand):
    opts: Any
    def execute(self: Any, args: Namespace) -> None: ...

class DeleteChannel(SecurityAwareCommand):
    opts: Any
    def execute(self: Any, args: Namespace) -> None: ...
