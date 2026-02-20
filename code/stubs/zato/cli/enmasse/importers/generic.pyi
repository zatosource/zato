from typing import Any, TYPE_CHECKING

import logging
from zato.cli.enmasse.util import preprocess_item
from zato.common.odb.model import GenericConn, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import set_instance_opaque_attrs
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.common.typing_ import any_, anydict, anylist, listtuple


class GenericConnectionImporter:
    connection_type: Any
    connection_defaults: Any
    connection_extra_field_defaults: Any
    connection_secret_keys: Any
    connection_required_attrs: Any
    importer: Any
    connection_defs: Any
    def __init__(self: Any, importer: EnmasseYAMLImporter) -> None: ...
    def _process_defs(self: Any, query_result: any_, out: dict) -> None: ...
    def get_defs_from_db(self: Any, session: SASession, cluster_id: int) -> anydict: ...
    def compare_defs(self: Any, yaml_defs: anylist, db_defs: anydict) -> tuple: ...
    def create_definition(self: Any, connection_def: anydict, session: SASession) -> any_: ...
    def update_definition(self: Any, connection_def: anydict, session: SASession) -> any_: ...
    def sync_definitions(self: Any, conn_list: anylist, session: SASession) -> listtuple: ...
