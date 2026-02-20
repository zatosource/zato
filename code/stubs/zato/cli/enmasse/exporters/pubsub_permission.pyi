from typing import Any, TYPE_CHECKING

import logging
from zato.common.api import PubSub
from zato.common.odb.query import pubsub_permission_list
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.typing_ import anydict, list_


class PubSubPermissionExporter:
    exporter: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> pubsub_permission_def_list: ...
