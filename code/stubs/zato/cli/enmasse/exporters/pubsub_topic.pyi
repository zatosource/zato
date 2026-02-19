from typing import Any

import logging
from zato.common.odb.query import pubsub_topic_list
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.typing_ import anydict, list_

class PubSubTopicExporter:
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> pubsub_topic_def_list: ...
