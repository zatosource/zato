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

class GenericConnectionImporter:

    connection_type = None
    connection_defaults = {}
    connection_extra_field_defaults = {}
    connection_secret_keys = ['password', 'secret', 'api_token']
    connection_required_attrs = ['name', 'address', 'username']

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            for key, default_value in cls.connection_defaults.items():
                if key not in item:
                    item[key] = default_value

            for key, default_value in cls.connection_extra_field_defaults.items():
                if key not in item:
                    item[key] = default_value

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
