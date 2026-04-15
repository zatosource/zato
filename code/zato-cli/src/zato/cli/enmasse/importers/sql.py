# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from uuid import uuid4

# Zato
from zato.cli.enmasse.util import get_engine_from_type, preprocess_item

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SQLImporter:

    sql_defaults = {
        'is_active': True,
        'pool_size': 10,
    }

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            for key, default_value in cls.sql_defaults.items():
                if key not in item:
                    item[key] = default_value

            if 'type' in item:
                item['engine'] = get_engine_from_type(item['type'])

            if 'password' not in item:
                item['password'] = uuid4().hex

            if 'extra' in item:
                extra = item['extra']
                if isinstance(extra, list):
                    item['extra'] = '\n'.join(str(elem) for elem in extra if elem)

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
