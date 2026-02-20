from typing import Any

import logging
from zato.common.api import GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query import email_smtp_list
from zato.common.util.sql import parse_instance_opaque_attr
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.typing_ import anydict, list_

class SMTPExporter:
    exporter: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def _should_skip_item(self: Any, item: Any, excluded_names: Any, excluded_prefixes: Any) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> list_[anydict]: ...
