from typing import Any, TYPE_CHECKING

from bunch import Bunch
from yaml import FullLoader, load as yaml_load
from zato.common.util.file_system import fs_safe_name
from zato.server.service import Service
from unittest import TestCase
from zato.common.typing_ import anydict


class CyMyService(Service):
    ...

def run_common_apispec_assertions(self: TestCase, data: str, with_all_paths: bool = ...) -> None: ...
