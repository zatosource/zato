# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

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
# ################################################################################################################################
