# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.common.api import ES, GENERIC

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class ElasticSearchImporter(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_ES

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_ES,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'is_outgoing': True,
        'pool_size': 1,

        # This one is a column on the ODB model rather than an opaque attribute
        'username': '',
    }

    # Note that timeout is not here because it is a column on the ODB model
    connection_extra_field_defaults = {
        'address_list': ES.Default.Address_List,
    }

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'address_list']

# ################################################################################################################################

    def _normalize_address_list(self, connection_def:'anydict') -> 'None':

        # In YAML, the addresses may be given as a list but the wrapper
        # expects a single newline-separated string.
        address_list = connection_def.get('address_list')
        if isinstance(address_list, list):
            connection_def['address_list'] = '\n'.join(address_list)

# ################################################################################################################################

    def create_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        self._normalize_address_list(connection_def)
        connection = super().create_definition(connection_def, session)

        # The timeout is a column on the ODB model rather than an opaque attribute
        connection.timeout = connection_def.get('timeout', ES.Default.Timeout)

        return connection

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        self._normalize_address_list(connection_def)

        # Let the base class update the opaque attributes first ..
        connection = super().update_definition(connection_def, session)

        # .. and then update the fields that are columns on the ODB model
        # .. rather than opaque attributes, but only if they are actually given on input.
        if 'username' in connection_def:
            connection.username = connection_def['username']

        if 'timeout' in connection_def:
            connection.timeout = connection_def['timeout']

        return connection

# ################################################################################################################################
# ################################################################################################################################
