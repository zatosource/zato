from typing import Any

import logging
import os
import socket
from zato.common.util.api import get_current_user
import sh

class _BaseRepoManager:
    repo_location: os.path.abspath
    def __init__(self: Any, repo_location: Any = ...) -> None: ...

class PassThroughRepoManager(_BaseRepoManager):
    def ensure_repo_consistency(self: Any) -> None: ...

class GitRepoManager(_BaseRepoManager):
    def ensure_repo_consistency(self: Any) -> None: ...
