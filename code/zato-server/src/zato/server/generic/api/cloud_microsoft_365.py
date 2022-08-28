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
from zato.server.connection.microsoft_365 import Microsoft365Client
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _Microsoft365Client:
    def __init__(self, config:'stranydict') -> 'None':

        # The actual connection object
        self.impl = Microsoft365Client.from_config(config)

        # Forward invocations to the underlying client
        self.get = self.impl.get
        self.post = self.impl.post
        self.ping = self.impl.ping

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
            conn = int()#_Microsoft365Client(self.config)
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

    def delete(self, ignored_reason=None):
        pass

# ################################################################################################################################
# ################################################################################################################################
