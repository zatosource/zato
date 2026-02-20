from typing import Any, TYPE_CHECKING

import os
import re
import string
from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path
from tempfile import gettempdir
from time import sleep
from uuid import uuid4
from zato.common.util.time_ import utcnow
from zato.common.typing_ import callable_, dictlist, strlist


def fs_safe_name(value: str) -> str: ...

def fs_safe_now(_utcnow: callable_ = ...) -> str: ...

def wait_for_file(path: str, max_wait: int = ...) -> None: ...

def get_tmp_path(prefix: str = ..., body: str = ..., suffix: str = ...) -> str: ...

def resolve_path(path: str, base_dir: str = ...) -> str: ...

def touch(path: str) -> None: ...

def touch_multiple(path_list: strlist) -> None: ...

def _walk_python_files(root_dir: str) -> None: ...

def touch_python_files(root_dir: str) -> None: ...

def get_python_files(root_dir: str) -> dictlist: ...
