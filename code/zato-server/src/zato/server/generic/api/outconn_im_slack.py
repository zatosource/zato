# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Slack
from slackclient import SlackClient

# Zato
from zato.common.util.http_ import get_proxy_config
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutconnIMSlackWrapper(Wrapper):
    """ Wraps a Slack connection client.
    """
    wrapper_type = 'Slack connection'

    def __init__(self, *args, **kwargs):
        super(OutconnIMSlackWrapper, self).__init__(*args, **kwargs)
        self._impl = None  # type: SlackClient

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            # Configuration of the underlying client
            client_config = {
                'token': self.config.secret,
                'proxies': get_proxy_config(self.config)
            }

            # Create the actual connection object
            self._impl = SlackClient(**client_config)

            # Confirm the connection was established
            self.ping()

            # We can assume we are connected now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        if self._impl.server.websocket:
            self._impl.server.websocket.close()

# ################################################################################################################################

    def _ping(self):
        out = self._impl.api_call('api.test')
        if not out['ok']:
            raise Exception(out['error'])

# ################################################################################################################################
# ################################################################################################################################
