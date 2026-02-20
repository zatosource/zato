from typing import Any, TYPE_CHECKING

import logging
from zato.common.api import GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter


class Microsoft365Importer(GenericConnectionImporter):
    connection_type: Any
    connection_defaults: Any
    connection_extra_field_defaults: Any
    connection_secret_keys: Any
    connection_required_attrs: Any
    def _process_scopes(self: Any, connection_def: Any) -> None: ...
    def _process_secret(self: Any, connection_def: Any) -> None: ...
    def create_definition(self: Any, connection_def: Any, session: Any) -> None: ...
    def update_definition(self: Any, connection_def: Any, session: Any) -> None: ...
