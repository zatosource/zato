# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from uuid import uuid4

# Bunch
from bunch import bunchify

# Zato
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelFTPWrapper(Wrapper):
    """ Represents an FTP channel.
    """
    wrapper_type = 'MongoDB connection'

    def __init__(self, *args, **kwargs):
        super(ChannelFTPWrapper, self).__init__(*args, **kwargs)
        self._client = None

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            #
            # ZZZ
            #
            # Create FTP channels here

            # Confirm the connection was established
            self.ping()

            # We can assume we are connected now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        self._client.close()

# ################################################################################################################################

    def _ping(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
