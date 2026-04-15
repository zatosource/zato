# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.common.api import GENERIC

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelOpenAPIImporter:

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'is_outgoing': False,
        'pool_size': 20,
        'recv_timeout': 250,
    }

    @classmethod
    def preprocess(cls, items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            for key, default_value in cls.connection_defaults.items():
                if key not in item:
                    item[key] = default_value

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
