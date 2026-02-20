from typing import Any, TYPE_CHECKING

from dataclasses import dataclass
from zato.common.typing_ import path_, pathlist


class HotDeployProject:
    sys_path_entry: path_
    pickup_from_path: pathlist
