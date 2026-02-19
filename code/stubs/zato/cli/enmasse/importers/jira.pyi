from typing import Any

from zato.common.api import GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

class JiraImporter(GenericConnectionImporter):
    connection_type: Any
    connection_defaults: Any
    connection_extra_field_defaults: Any
    connection_secret_keys: Any
    connection_required_attrs: Any
