from typing import Any, TYPE_CHECKING

from contextlib import closing
from logging import getLogger
from zato.bunch import Bunch
from zato.common.const import SECRETS, ServiceConst
from zato.common.util.config import resolve_name
from zato.common.util.sql import elems_with_opaque
from zato.common.util.url_dispatcher import get_match_target
from zato.server.config import ConfigDict
from zato.url_dispatcher import Matcher
from zato.common.odb.model import Server as ServerModel
from zato.common.typing_ import anydict, anydictnone, anyset
from zato.server.base.parallel import ParallelServer


class ModuleCtx:
    Config_Store: Any

class ConfigLoader:
    def set_up_security(self: ParallelServer, cluster_id: int) -> None: ...
    def set_up_config(self: ParallelServer, server: ServerModel) -> None: ...
    def _after_init_accepted(self: ParallelServer, locally_deployed: Any) -> None: ...
    def get_config_odb_data(self: Any, parallel_server: ParallelServer) -> Bunch: ...
    def _encrypt_secrets(self: ParallelServer) -> None: ...
    def _after_init_non_accepted(self: Any, server: ParallelServer) -> None: ...
