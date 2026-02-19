from typing import Any

import errno
import os
import sys
import ctypes
import ctypes.util

def sendfile(fdout: Any, fdin: Any, offset: Any, nbytes: Any) -> None: ...
