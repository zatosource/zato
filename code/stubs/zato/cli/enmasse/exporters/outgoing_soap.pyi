from typing import Any, TYPE_CHECKING

import logging
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.odb.model import to_json
from zato.common.odb.query import http_soap_list
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.typing_ import anydict, list_


class OutgoingSOAPExporter:
    exporter: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> outgoing_soap_def_list: ...
