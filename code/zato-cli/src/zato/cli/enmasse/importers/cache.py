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

class CacheImporter:

    cache_defaults = {
        'is_active': True,
        'is_default': False,
        'max_size': 10000,
        'max_item_size': 1000000,
        'extend_expiry_on_get': True,
        'extend_expiry_on_set': False,
        'sync_method': 'in-background',
        'persistent_storage': 'sqlite',
    }

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            for key, default_value in cls.cache_defaults.items():
                if key not in item:
                    item[key] = default_value

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
