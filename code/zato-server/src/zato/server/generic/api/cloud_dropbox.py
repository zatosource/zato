# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Dropbox
from dropbox import create_session, Dropbox as DropboxClient

# Zato
from zato.common.util.api import parse_extra_into_dict
from zato.common.util.eval_ import as_list
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CloudDropbox(Wrapper):
    """ Wraps a Dropbox connection client.
    """
    wrapper_type = 'Dropbox connection'
    required_secret_attr = 'secret'
    required_secret_label = 'an OAuth 2 access token'

    def __init__(self, *args, **kwargs):
        super(CloudDropbox, self).__init__(*args, **kwargs)
        self._impl = None  # type: DropboxClient

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            # Create a pool of at most that many connections
            session = create_session(50)

            scope = as_list(self.config.default_scope, ',')

            config = {
                'session': session,
                'user_agent': self.config.user_agent,
                'oauth2_access_token': self.server.decrypt(self.config.secret),
                'oauth2_access_token_expiration': int(self.config.oauth2_access_token_expiration or 0),
                'scope': scope,
                'max_retries_on_error': int(self.config.max_retries_on_error or 0),
                'max_retries_on_rate_limit': int(self.config.max_retries_on_rate_limit or 0),
                'timeout': int(self.config.timeout),
                'headers': parse_extra_into_dict(self.config.http_headers),
            }

            # Create the actual connection object
            self._impl = DropboxClient(**config)

            # Confirm the connection was established
            self.ping()

            # We can assume we are connected now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        if self._impl:
            self._impl.close()

# ################################################################################################################################

    def _ping(self):
        self._impl.check_user()

# ################################################################################################################################
# ################################################################################################################################
