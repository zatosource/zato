# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import OK
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import bunchify

# Requests
import requests

# Zato
from zato.common.json_internal import loads
from zato.common.util.http_ import get_proxy_config
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################

if 0:
    from requests import Response

    Response = Response


# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################


class TelegramClient:
    def __init__(self, address, token, connect_timeout, invoke_timeout, proxies):
        # type: (str, str, int, int, dict)

        self.address = address.replace('{token}', token)
        self.token = token
        self.connect_timeout = connect_timeout
        self.invoke_timeout = invoke_timeout

        self.session = requests.Session()
        self.session.proxies = proxies

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
            logger.warning('Could not invoke Telegram API, e:`%s`', format_exc())
            raise

# ################################################################################################################################

    def ping(self):
        return self.invoke('getMe')

# ################################################################################################################################
# ################################################################################################################################

class OutconnIMTelegramWrapper(Wrapper):
    """ Wraps a Telegram connection client.
    """
    wrapper_type = 'Telegram connection'

    def __init__(self, *args, **kwargs):
        super(OutconnIMTelegramWrapper, self).__init__(*args, **kwargs)
        self._impl = None  # type: TelegramClient

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            # Configuration of the underlying client
            client_config = {
                'address': self.config.address,
                'connect_timeout': self.config.connect_timeout,
                'invoke_timeout': self.config.invoke_timeout,
                'token': self.config.secret or '<default-empty-telegram-token>',
                'proxies': get_proxy_config(self.config),
            }

            # Create the actual connection object
            self._impl = TelegramClient(**client_config)

            # Confirm the connection was established
            self.ping()

            # We can assume we are connected now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        self._impl.session.close()

# ################################################################################################################################

    def _ping(self):
        return self._impl.ping()

# ################################################################################################################################
# ################################################################################################################################
