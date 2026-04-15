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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SMTPImporter:

    smtp_defaults = {
        'is_active': True,
        'timeout': 60,
        'is_debug': False,
        'mode': 'plain',
        'ping_address': '',
    }

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            for key, default_value in cls.smtp_defaults.items():
                if key not in item:
                    item[key] = default_value

            if 'username' not in item or item['username'] is None:
                item['username'] = ''

            if 'password' not in item:
                item['password'] = uuid4().hex

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
