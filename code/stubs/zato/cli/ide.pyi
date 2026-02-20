from typing import Any, TYPE_CHECKING

import os
from contextlib import closing
from zato.cli import ManageCommand
from zato.common.const import SECRETS
from zato.common.util.api import get_odb_session_from_server_dir
from zato.cli.util import run_cli_command
import sys
from zato.common.api import IDEDeploy
from zato.common.crypto.api import CryptoManager, ServerCryptoManager
from zato.common.odb.model import HTTPBasicAuth
from zato.common.util.cli import CommandLineServiceInvoker


class SetIDEPassword(ManageCommand):
    opts: Any
    def is_password_required(self: Any) -> None: ...
    def execute(self: Any, args: Any) -> None: ...
