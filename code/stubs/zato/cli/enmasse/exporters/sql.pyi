from typing import Any

import logging
from zato.cli.enmasse.util import get_type_from_engine
from zato.common.odb.model import to_json
from zato.common.odb.query import out_sql_list
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.odb.model import SQLConnectionPool
from zato.common.typing_ import anydict, list_

class SQLExporter:
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> sql_def_list: ...
