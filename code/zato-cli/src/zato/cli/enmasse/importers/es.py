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

class ElasticSearchImporter:

    es_defaults = {
        'is_active': True,
        'timeout': 90,
        'body_as': 'POST',
    }

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            for key, default_value in cls.es_defaults.items():
                if key not in item:
                    item[key] = default_value

            if 'host' in item and 'hosts' not in item:
                item['hosts'] = item.pop('host')

            if isinstance(item.get('hosts'), list):
                item['hosts'] = '\n'.join(item['hosts'])

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
