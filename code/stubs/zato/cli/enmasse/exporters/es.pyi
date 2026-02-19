from typing import Any

import logging
from zato.common.api import GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query import search_es_list
from zato.common.util.sql import parse_instance_opaque_attr
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.typing_ import list_

class ElasticSearchExporter:
    DIRECT_FIELDS: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export_es(self: Any, session: SASession) -> list_: ...
