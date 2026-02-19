from typing import Any

import importlib
import sys
import traceback
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from logging import getLogger
from pathlib import Path
from threading import current_thread
from zato.common.typing_ import cast_, module_
from zato.common.typing_ import intnone

class ModuleInfo:
    name: str
    path: Path
    module: module_

def get_python_id(item: Any) -> None: ...

def get_current_stack() -> None: ...

def log_current_stack() -> None: ...

def get_full_stack() -> None: ...

def reload_module_(mod_name: str) -> None: ...

def get_module_name_by_path(path: str | Path) -> str: ...

def import_module_by_path(path: str) -> ModuleInfo | None: ...
