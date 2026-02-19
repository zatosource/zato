from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
import os
from zato.common.api import SCHEDULER
from zato.common.crypto.api import WebAdminCryptoManager
from zato.common.crypto.secret_key import resolve_secret_key
from zato.common.util.cli import read_stdin_data

def update_globals(config: Any, base_dir: Any = ..., needs_crypto: Any = ...) -> None: ...
