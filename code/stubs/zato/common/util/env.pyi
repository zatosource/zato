from typing import Any

from zato.common.typing_ import any_, strlist, strlistnone
import os
from logging import getLogger
from zato.common.util.api import make_list_from_string_list
from zato.common.ext.configobj_ import ConfigObj

def populate_environment_from_file(env_path: str) -> strlist: ...

def get_list_from_environment(key: str, separator: str) -> strlist: ...
