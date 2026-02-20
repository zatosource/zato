from typing import Any, TYPE_CHECKING

from argparse import Namespace
from zato.common.typing_ import any_, anydict
import pyotp
from zato.common.crypto.totp_ import TOTPManager
from zato.common.api import TOTP
import os
from bunch import Bunch


def get_totp_info_from_args(args: Any, default_key_label: Any = ...) -> None: ...

def run_cli_command(command_class: any_, config: anydict, path: any_) -> None: ...
