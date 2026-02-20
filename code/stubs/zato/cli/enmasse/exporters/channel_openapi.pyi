from typing import Any, TYPE_CHECKING

import logging
from zato.common.api import CONNECTION, GENERIC, URL_TYPE
from zato.common.odb.model import HTTPSOAP, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.typing_ import anydict, list_


class ChannelOpenAPIExporter:
    exporter: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> channel_openapi_def_list: ...
    def _get_rest_channels_map(self: Any, session: SASession, cluster_id: int) -> dict: ...
