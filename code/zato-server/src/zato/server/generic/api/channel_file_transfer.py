# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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
    needs_self_client = False
    wrapper_type = 'File transfer channel'
    build_if_not_active = True

    def __init__(self, *args, **kwargs):
        super(ChannelFileTransferWrapper, self).__init__(*args, **kwargs)
        self._impl = None

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            # Create a new observer ..
            self.server.worker_store.file_transfer_api.create(self.config)

            # .. and start it now.
            self.server.worker_store.file_transfer_api.start_observer(self.config.name)

            # We can assume we are done building the channel now
            self.is_connected = True

# ################################################################################################################################

    def delete(self):
        """ This is overridden from Wrapper.delete because we do not have self._impl.
        """
        self.server.worker_store.file_transfer_api.delete(self.config)

# ################################################################################################################################

    def _ping(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
