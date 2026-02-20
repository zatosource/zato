from typing import Any

import os
import os.path
import re
import sys
import time
import threading
from inotify.adapters import Inotify
import inotify.constants

class Reloader(threading.Thread):
    _extra_files: set
    _extra_files_lock: threading.RLock
    _interval: Any
    _callback: Any
    def __init__(self: Any, extra_files: Any = ..., interval: Any = ..., callback: Any = ...) -> None: ...
    def add_extra_file(self: Any, filename: Any) -> None: ...
    def get_files(self: Any) -> None: ...
    def run(self: Any) -> None: ...
