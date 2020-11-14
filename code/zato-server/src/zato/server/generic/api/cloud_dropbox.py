# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Dropbox
from dropbox import Dropbox as DropboxClient

# Zato
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CloudDropbox(Wrapper):
    """ Wraps a Dropbox connection client.
    """
    wrapper_type = 'Dropbox connection'

    def __init__(self, *args, **kwargs):
        super(CloudDropbox, self).__init__(*args, **kwargs)
        self._client = None  # type: DropboxClient

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            # Create the actual connection object
            self._client = DropboxClient(self.config.oauth2_access_token)

            # Confirm the connection was established
            self.ping()

            # We can assume we are connected now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        pass

# ################################################################################################################################

    def _ping(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
