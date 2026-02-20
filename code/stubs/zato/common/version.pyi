from typing import Any, TYPE_CHECKING

import platform
import os
import sys
from zato.common.py23_.past.builtins import execfile
import distro


def get_sys_info() -> None: ...

def get_version() -> None: ...
