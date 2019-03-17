# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Slack
from slackclient import SlackClient

# Zato
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
        self._client = None  # type: SlackClient

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            # Proxy configuration, if any
            if self.config.http_proxy_list or self.config.https_proxy_list:
                proxy_config = {}

                if self.config.http_proxy_list:
                    proxy_config['http'] = self.config.http_proxy_list.splitlines()

                if self.config.https_proxy_list:
                    proxy_config['https'] = self.config.https_proxy_list.splitlines()

            else:
                proxy_config = None

            # Configuration of the underlying client
            client_config = {
                'token': self.config.secret,
                'proxies': proxy_config
            }

            # Create the actual connection object
            self._client = SlackClient(**client_config)

            # Confirm the connection was established
            self.ping()

            # We can assume we are connected now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        if self._client.server.websocket:
            self._client.server.websocket.close()

# ################################################################################################################################

    def _ping(self):
        out = self._client.api_call('api.test')
        if not out['ok']:
            raise Exception(out['error'])

# ################################################################################################################################
# ################################################################################################################################
