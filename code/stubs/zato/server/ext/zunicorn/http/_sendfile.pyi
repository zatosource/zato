from typing import Any, TYPE_CHECKING

import errno
import os
import sys
import ctypes
import ctypes.util

_sendfile = _libc.sendfile

def sendfile(fdout: Any, fdin: Any, offset: Any, nbytes: Any) -> None: ...
