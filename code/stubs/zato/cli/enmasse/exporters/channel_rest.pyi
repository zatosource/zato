from typing import Any

import logging
from contextlib import closing
from sqlalchemy import and_, select
from zato.common.api import CONNECTION, Groups, MISC, URL_TYPE
from zato.common.odb.model import GenericObject, to_json
from zato.common.odb.query import http_soap_list
from zato.common.util.sql import elems_with_opaque
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.typing_ import anydict, list_

class ChannelExporter:
    exporter: Any
    group_id_to_name: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def _load_security_groups(self: Any, session: SASession, cluster_id: int) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> channel_def_list: ...
