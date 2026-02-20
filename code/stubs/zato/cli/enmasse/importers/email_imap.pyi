from typing import Any, TYPE_CHECKING

import logging
from uuid import uuid4
from zato.cli.enmasse.util import preprocess_item
from zato.common.api import EMAIL as EMail_Common
from zato.common.odb.model import IMAP, to_json
from zato.common.odb.query import email_imap_list
from zato.common.util.sql import set_instance_opaque_attrs
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.common.typing_ import any_, anydict, anylist, listtuple


class IMAPImporter:
    importer: Any
    imap_defs: Any
    def __init__(self: Any, importer: EnmasseYAMLImporter) -> None: ...
    def _process_imap_defs(self: Any, query_result: any_, out: dict) -> None: ...
    def get_imap_defs_from_db(self: Any, session: SASession, cluster_id: int) -> anydict: ...
    def compare_imap_defs(self: Any, yaml_defs: anylist, db_defs: anydict) -> tuple: ...
    def create_imap_definition(self: Any, imap_def: anydict, session: SASession) -> any_: ...
    def update_imap_definition(self: Any, imap_def: anydict, session: SASession) -> any_: ...
    def sync_imap_definitions(self: Any, imap_list: anylist, session: SASession) -> listtuple: ...
