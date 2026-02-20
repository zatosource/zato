from typing import Any, TYPE_CHECKING

import os
from zato.common.util.platform_ import is_non_windows
from zato.common.typing_ import intlist, strlist


def parse_extra_into_list(data: str) -> intlist: ...

def path_string_to_list(base_dir: str, data: str) -> strlist: ...

def path_string_list_to_list(base_dir: str, data: str | strlist) -> strlist: ...
