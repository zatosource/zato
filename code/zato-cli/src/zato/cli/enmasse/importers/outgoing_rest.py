# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import preprocess_item

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingRESTImporter:

    outgoing_rest_defaults = {
        'is_active': True,
        'ping_method': 'GET',
        'pool_size': 20,
        'timeout': 60,
    }

    connection_extra_field_defaults = {
        'validate_tls': True,
    }

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            if 'tls_verify' in item:
                item['validate_tls'] = item.pop('tls_verify')

            for key, default_value in cls.outgoing_rest_defaults.items():
                if key not in item:
                    item[key] = default_value

            for key, default_value in cls.connection_extra_field_defaults.items():
                if key not in item:
                    item[key] = default_value

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
