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

'''
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import OK
from json import loads
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import bunchify

# Requests
import requests

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # Requests
    from requests.models import Response

    # For pyflakes
    Response = Response

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################


class TelegramAPI(object):
    def __init__(self, address, token, connect_timeout, invoke_timeout):
        # type: (unicode, unicode, int, int)

        self.address = address.replace('{token}', token)
        self.token = token
        self.connect_timeout = connect_timeout
        self.invoke_timeout = invoke_timeout

        self.session = requests.Session()

# ################################################################################################################################

    def _invoke(self, method, data=None, *args, **kwargs):
        to_bunch = kwargs.get('to_bunch', True)
        result = self.session.post(self.address.format(method=method), data=data, *args, **kwargs) # type: Response

        if not result.status_code == OK:
            raise Exception(result.text)

        if to_bunch:
            out = loads(result.text)
            return bunchify(out)
        else:
            return result

# ################################################################################################################################

    def invoke(self, *args, **kwargs):
        try:
            return self._invoke(*args, **kwargs)
        except Exception:
            logger.warn('Could not invoke Telegram API, e:`%s`', format_exc())
            raise

# ################################################################################################################################

    def ping(self):
        return self.invoke('getMe1')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    base_address = 'https://api.telegram.org/bot{token}/{method}'
    token = '....'
    connect_timeout = 5
    invoke_timeout = 5

    api = TelegramAPI(base_address, token, connect_timeout, invoke_timeout)
    out = api.ping()
    print(111, out, type(out))
'''
