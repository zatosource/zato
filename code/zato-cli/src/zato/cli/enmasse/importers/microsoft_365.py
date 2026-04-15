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
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365Importer(GenericConnectionImporter):

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
        'recv_timeout': 250,
    }

    connection_secret_keys = ['secret', 'secret_value', 'password']
    connection_required_attrs = ['name', 'client_id', 'tenant_id']

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:

            # Run the parent class preprocessing first
            preprocessed = super().preprocess([item])
            item = preprocessed[0]

            scopes = item.get('scopes')
            if isinstance(scopes, list):
                item['scopes'] = '\n'.join(scopes)

            for key in ['secret', 'password']:
                if value := item.get(key):
                    item['secret_value'] = value
                    break

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
