# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelFileTransferWrapper(Wrapper):
    """ Represents a file transfer channel.
    """
    wrapper_type = 'File transfer channel'

    def __init__(self, *args, **kwargs):
        super(ChannelFileTransferWrapper, self).__init__(*args, **kwargs)
        self._client = None

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            #
            # ZZZ
            #
            # Create file transfer channels here

            logger.warn('WRAPPER._init_impl %s', self.config)

            # We can assume we are done building the channel now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        self._client.close()

# ################################################################################################################################

    def _ping(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
