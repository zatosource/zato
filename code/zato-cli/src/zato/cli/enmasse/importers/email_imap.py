# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from uuid import uuid4

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.common.api import EMAIL as EMail_Common

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class IMAPImporter:

    imap_defaults = {
        'is_active': True,
        'port': 143,
        'timeout': 30,
        'debug_level': 0,
        'mode': 'plain',
        'get_criteria': '{}',
        'filter_criteria': 'isRead ne true',
    }

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            for key, default_value in cls.imap_defaults.items():
                if key not in item:
                    item[key] = default_value

            if 'type' in item:
                if item['type'] == 'microsoft-365':
                    item['server_type'] = EMail_Common.IMAP.ServerType.Microsoft365
                else:
                    item['server_type'] = item['type']
            else:
                item['server_type'] = EMail_Common.IMAP.ServerType.Generic

            if 'password' not in item:
                item['password'] = uuid4().hex

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
