# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingGraphQLImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'extra': None,
        'pool_size': 1,
    }

    connection_extra_field_defaults = {
        'default_query_timeout': 60,
    }

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'address']

# ################################################################################################################################

    def _resolve_security(self, connection_def:'anydict') -> 'None':
        """ Resolves a security name to security_id and auth_type,
        storing them in the connection_def for opaque1 persistence.
        """
        security_name = connection_def.get('security')
        if not security_name:
            return

        if security_name not in self.importer.sec_defs:
            raise Exception(f'Security definition "{security_name}" not found for GraphQL connection "{connection_def["name"]}"')

        sec_def = self.importer.sec_defs[security_name]

        connection_def['security_id'] = sec_def['id']
        connection_def['security_name'] = security_name
        connection_def['auth_type'] = sec_def['type']

        # .. remove the 'security' key so it doesn't interfere with GenericConnection ..
        del connection_def['security']

# ################################################################################################################################

    def create_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
        self._resolve_security(connection_def)
        return super().create_definition(connection_def, session)

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
        self._resolve_security(connection_def)
        return super().update_definition(connection_def, session)
