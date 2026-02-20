from typing import Any, TYPE_CHECKING

import logging
from zato.common.odb.model import PubSubSubscription, PubSubSubscriptionTopic, PubSubTopic, SecurityBase, HTTPSOAP
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.typing_ import anydict, strlist


class PubSubSubscriptionExporter:
    exporter: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> pubsub_subscription_def_list: ...
