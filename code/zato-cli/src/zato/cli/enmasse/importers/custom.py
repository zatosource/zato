# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli.enmasse.client import get_sdk_secret_field_names
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.cli.enmasse.util.secrets import get_server_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, strtuple

# ################################################################################################################################
# ################################################################################################################################

# Declared fields with these names are backed by database columns rather than opaque attributes,
# both here and when a definition is created through the server's API.
column_fields = ('address', 'port', 'timeout', 'pool_size', 'username', 'data_format')

# ################################################################################################################################
# ################################################################################################################################

def custom_key_to_connection_type(yaml_key:'str') -> 'str':
    """ Maps a top-level YAML key to the full connection type, e.g. custom_crm becomes outconn-crm.
    """
    short_type = yaml_key[len(ModuleCtx.Custom_Key_Prefix):]
    out = ModuleCtx.Custom_Type_Prefix + short_type
    return out

# ################################################################################################################################

def connection_type_to_custom_key(type_:'str') -> 'str':
    """ Maps a full connection type to its top-level YAML key, e.g. outconn-crm becomes custom_crm.
    """
    short_type = type_[len(ModuleCtx.Custom_Type_Prefix):]
    out = ModuleCtx.Custom_Key_Prefix + short_type
    return out

# ################################################################################################################################
# ################################################################################################################################

class CustomConnectorImporter(GenericConnectionImporter):
    """ Imports definitions of one custom connector type built with the Connector SDK.
    An instance is built per top-level YAML key, e.g. custom_crm, and all the fields
    a definition carries beyond the name are stored as the connection's opaque attributes.
    """

    # Only the name is required - the other fields are whatever the connector class declares.
    connection_required_attrs = ['name']

    # Nothing is moved to the secret column - all the declared fields of a custom connector
    # live in its opaque attributes.
    connection_secret_keys = []

    def __init__(self, importer:'EnmasseYAMLImporter', yaml_key:'str') -> 'None':
        super().__init__(importer)

        # E.g. custom_crm
        self.yaml_key = yaml_key

        # E.g. outconn-crm
        self.connection_type = custom_key_to_connection_type(yaml_key)

        # The column-backed attributes every definition of the type gets.
        self.connection_defaults = {
            'type_': self.connection_type,
            'is_active': True,
            'is_internal': False,
            'is_channel': False,
            'is_outconn': True,
        }

        # The names of the Secret fields the connector class declares, once the running server has been asked
        self.secret_field_names:'strtuple | None' = None

# ################################################################################################################################

    def get_opaque_secret_keys(self, session:'SASession') -> 'strtuple':
        """ Returns the names of the Secret fields the connector class declares. Only the running server knows
        the class, so it is asked once per type. A server that cannot be reached fails the import - an SDK connector
        type cannot exist without a server and an import must not guess.
        """
        if self.secret_field_names is None:
            server_dir = get_server_dir(session)
            self.secret_field_names = get_sdk_secret_field_names(server_dir, self.connection_type)

        return self.secret_field_names

# ################################################################################################################################

    def _get_column_secret_keys(self, opaque_secret_keys:'strtuple') -> 'strtuple':
        """ Nothing is moved to the secret column, so no declared field ever leaves the opaque attributes.
        """
        return ()

# ################################################################################################################################

    def _set_column_fields(self, connection:'any_', connection_def:'anydict') -> 'None':
        """ Sets the declared fields that are backed by database columns - the base class
        stores everything else in the opaque attributes, which never include column names.
        """
        for name in column_fields:
            if name in connection_def:
                setattr(connection, name, connection_def[name])

# ################################################################################################################################

    def create_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
        connection = super().create_definition(connection_def, session)
        self._set_column_fields(connection, connection_def)
        return connection

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
        connection = super().update_definition(connection_def, session)
        self._set_column_fields(connection, connection_def)
        return connection

# ################################################################################################################################
# ################################################################################################################################
