# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.typing_ import cast_
from zato.server.connection.queue import Wrapper

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

class _Microsoft365Client:
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

        opaque1 = config.pop('opaque1', '{}')
        opaque1 = loads(opaque1)
        config.update(opaque1)

        scopes = config.get('scopes') or []

        tenant_id = config['tenant_id']
        client_id = config['client_id']
        secret_value = config['secret_value']

        credentials = (client_id, secret_value)

        account = Account(credentials, auth_flow_type='credentials', tenant_id=tenant_id)
        account.authenticate(scopes=scopes)

        return account

# ################################################################################################################################

    def ping(self):
        result = self.impl.get_current_user()
        logger.info('Microsoft 365 ping result (%s) -> `%s`', self.config['name'], result)

# ################################################################################################################################
# ################################################################################################################################

class CloudMicrosoft365Wrapper(Wrapper):
    """ Wraps a queue of connections to Microsoft 365.
    """
    def __init__(self, config:'stranydict', server) -> 'None':
        config['auth_url'] = config['address']
        super(CloudMicrosoft365Wrapper, self).__init__(config, 'Microsoft 365', server)

# ################################################################################################################################

    def add_client(self):

        try:
            conn = _Microsoft365Client(self.config)
            self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding a Microsoft 365 client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self):
        with self.client() as client:
            client = cast_('_Microsoft365Client', client)
            client.ping()

# ################################################################################################################################
# ################################################################################################################################
