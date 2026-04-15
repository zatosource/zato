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

class SecurityImporter:

    @staticmethod
    def preprocess(items:'anylist') -> 'anylist':

        out = []

        for item in items:
            item = preprocess_item(item)

            if 'auth_endpoint' in item:
                item['auth_server_url'] = item.pop('auth_endpoint')

            sec_type = item.get('type', '')

            if sec_type == 'apikey' and 'username' not in item:
                item['username'] = f'Zato-Not-Used-{uuid4().hex}'

            if sec_type == 'apikey' and 'header' not in item:
                item['header'] = 'X-API-Key'

            if 'password' not in item:
                item['password'] = f'Zato-Auto-Password-{uuid4().hex}'

            if sec_type == 'bearer_token':
                if 'client_id_field' not in item:
                    item['client_id_field'] = 'client_id'
                if 'client_secret_field' not in item:
                    item['client_secret_field'] = 'client_secret'
                if 'grant_type' not in item:
                    item['grant_type'] = 'client_credentials'
                if 'data_format' not in item:
                    item['data_format'] = 'form'

            out.append(item)

        return out

# ################################################################################################################################
# ################################################################################################################################
