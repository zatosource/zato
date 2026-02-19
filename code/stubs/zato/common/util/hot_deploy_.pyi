from typing import Any

import os
from logging import getLogger
from pathlib import Path
from zato.common.api import HotDeploy
from zato.common.hot_deploy_ import HotDeployProject, pickup_order_patterns
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool
from zato.common.util.env import get_list_from_environment
from zato.common.util.file_system import resolve_path
from zato.common.typing_ import iterator_, list_, pathlist, strdictdict

def get_project_info(root: Any, src_dir_name: Any) -> list_[HotDeployProject] | None: ...

def extract_pickup_from_items(base_dir: Any, pickup_config: Any, src_dir_name: Any) -> iterator_[str | list_[HotDeployProject]]: ...
