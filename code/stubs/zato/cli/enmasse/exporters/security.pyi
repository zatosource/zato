from typing import Any, TYPE_CHECKING

import logging
from zato.common.json_internal import loads
from zato.common.odb.model import to_json
from zato.common.odb.query import basic_auth_list, apikey_security_list, ntlm_list, oauth_list
from zato.common.util.sql import parse_instance_opaque_attr
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.typing_ import anydict, list_


class SecurityExporter:
    exporter: Any
    def __init__(self: Any, exporter: EnmasseYAMLExporter) -> None: ...
    def _should_skip_item(self: Any, item: Any, excluded_names: Any, excluded_prefixes: Any) -> None: ...
    def _process_standard_security(self: Any, items: Any, sec_type: Any, excluded_names: Any, excluded_prefixes: Any) -> None: ...
    def _process_bearer_tokens(self: Any, items: Any, excluded_names: Any, excluded_prefixes: Any) -> None: ...
    def export(self: Any, session: SASession, cluster_id: int) -> list_[anydict]: ...
