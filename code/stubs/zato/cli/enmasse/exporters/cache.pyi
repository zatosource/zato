from typing import Any

import logging
from zato.common.odb.query import cache_builtin_list
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.odb.model import CacheBuiltin
from zato.common.typing_ import anydict, list_

class CacheExporter:
    exporter: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> cache_def_list: ...
