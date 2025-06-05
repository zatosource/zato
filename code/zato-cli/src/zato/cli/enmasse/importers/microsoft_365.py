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

logger = logging.getLogger(__name__)

class Microsoft365Importer(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': False,
        'is_outgoing': True,
        'pool_size': 20,
        'timeout': 250,
    }

    connection_extra_field_defaults = {
        'tenant_id': None,
        'client_id': None,
        'secret_value': None,
        'scopes': None,
        'recv_timeout': 250
    }

    connection_secret_keys = ['secret_value']
    connection_required_attrs = ['name', 'client_id', 'tenant_id']

# ################################################################################################################################

    def _process_scopes(self, connection_def):

        scopes = connection_def.get('scopes')

        # If scopes is a list, convert it to a newline-delimited string
        if isinstance(scopes, list):
            connection_def['scopes'] = '\n'.join(scopes)

        return connection_def

# ################################################################################################################################

    def create_definition(self, connection_def, session):
        connection_def = self._process_scopes(connection_def)
        return super().create_definition(connection_def, session)

# ################################################################################################################################

    def update_definition(self, connection_def, session):
        connection_def = self._process_scopes(connection_def)
        return super().update_definition(connection_def, session)

# ################################################################################################################################
# ################################################################################################################################
