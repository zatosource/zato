from typing import Any, TYPE_CHECKING

from zato.common.api import GENERIC, LDAP
from zato.cli.enmasse.importers.generic import GenericConnectionImporter


class LDAPImporter(GenericConnectionImporter):
    connection_type: Any
    connection_defaults: Any
    connection_extra_field_defaults: Any
    connection_secret_keys: Any
    connection_required_attrs: Any
