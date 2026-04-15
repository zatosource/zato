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

class OutgoingSOAPImporter:

    soap_defaults = {
        'is_active': True,
        'soap_action': '',
        'soap_version': '1.1',
        'ping_method': 'GET',
        'pool_size': 20,
        'timeout': 60,
        'merge_url_params_req': True,
        'has_rbac': False,
        'tls_verify': True,
        'is_internal': False,
    }

    connection_extra_field_defaults = {
        'validate_tls': True,
    }

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            for key, default_value in cls.soap_defaults.items():
                if key not in item:
                    item[key] = default_value

            for key, default_value in cls.connection_extra_field_defaults.items():
                if key not in item:
                    item[key] = default_value

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
