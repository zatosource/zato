from typing import Any

import logging
from zato.common.api import ODOO
from zato.common.odb.model import to_json
from zato.common.odb.query import out_odoo_list
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.odb.model import OutgoingOdoo
from zato.common.typing_ import anydict, list_

class OdooExporter:
    exporter: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> odoo_def_list: ...
