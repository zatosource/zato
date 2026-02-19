from typing import Any

import logging
from sqlalchemy import and_, select
from zato.common.api import Groups
from zato.common.odb.model import GenericObject, SecurityBase
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.typing_ import anydict, list_

class GroupExporter:
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> group_def_list: ...
    def _get_security_name_from_reference(self: Any, session: SASession, reference: str, cluster_id: int) -> str: ...
