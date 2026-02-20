from typing import Any, TYPE_CHECKING

import logging
from copy import deepcopy
from zato.cli.enmasse.util import assign_security, preprocess_item, security_needs_update
from zato.common.api import CONNECTION, HTTP_SOAP_SERIALIZATION_TYPE, URL_TYPE
from zato.common.odb.model import HTTPSOAP, to_json
from zato.common.util.sql import set_instance_opaque_attrs
from sqlalchemy.orm.session import Session as SASession
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.common.typing_ import any_, anydict, anylist, listtuple


class OutgoingSOAPImporter:
    importer: Any
    connection_defs: Any
    def __init__(self: Any, importer: EnmasseYAMLImporter) -> None: ...
    def get_outgoing_soap_from_db(self: Any, session: SASession, cluster_id: int) -> anydict: ...
    def compare_outgoing_soap(self: Any, yaml_defs: anylist, db_defs: anydict) -> listtuple: ...
    def create_outgoing_soap(self: Any, outgoing_def: anydict, session: SASession) -> any_: ...
    def update_outgoing_soap(self: Any, outgoing_def: anydict, session: SASession) -> any_: ...
    def sync_outgoing_soap(self: Any, outgoing_list: anylist, session: SASession) -> listtuple: ...
