# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    from O365 import Account as Office365Account
    Office365Account = Office365Account

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365Client:
    def __init__(self, config:'stranydict') -> 'None':

        self.config = config
        self.impl = self.impl_from_config(config)
        self.ping()

# ################################################################################################################################

    def impl_from_config(self, config:'stranydict') -> 'Office365Account':

        # stdlib
        from json import loads

        # Office-365
        from O365 import Account

        opaque1 = config.pop('opaque1', None) or '{}'
        opaque1 = loads(opaque1)
        config.update(opaque1)

        scopes = config.get('scopes') or []

        tenant_id = config['tenant_id']
        client_id = config['client_id']
        secret_value = config.get('secret_value') or config.get('secret') or config['password']

        credentials = (client_id, secret_value)

        account = Account(credentials, auth_flow_type='credentials', tenant_id=tenant_id)
        _ = account.authenticate(scopes=scopes)

        return account

# ################################################################################################################################

    def api(self) -> 'Office365Account':
        out = self.impl_from_config(self.config)
        return out

# ################################################################################################################################

    def ping(self):
        result = self.impl.get_current_user()
        logger.info('Microsoft 365 ping result (%s) -> `%s`', self.config['name'], result)

# ################################################################################################################################
# ################################################################################################################################
