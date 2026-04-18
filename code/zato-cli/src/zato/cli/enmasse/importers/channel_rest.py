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

class ChannelImporter:

    channel_defaults = {
        'is_active': True,
        'merge_url_params_req': True,
        'match_slash': True,
        'content_encoding': '',
        'cache_type': None,
        'cache_name': '',
        'cache_expiry': 0,
        'data_format': 'json',
        'transport': 'plain_http',
        'connection': 'channel',
        'soap_action': '',
        'soap_version': None,
        'sec_type': None,
        'security_id': None,
        'security_name': None,
        'is_internal': False,
        'serialization_type': 'string',
    }

    @staticmethod
    def preprocess(items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            for key, default_value in ChannelImporter.channel_defaults.items():
                if key not in item:
                    item[key] = default_value

            if 'service_name' not in item and 'service' in item:
                item['service_name'] = item['service']
            item.setdefault('service_name', '')
            item.setdefault('service_id', None)

            if 'gateway_service_list' in item:
                gw_list = item['gateway_service_list']
                if isinstance(gw_list, str):
                    item['gateway_service_list'] = [s.strip() for s in gw_list.strip().split('\n') if s.strip()]

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
