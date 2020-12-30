# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

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

class ChannelHL7MLLPWrapper(Wrapper):
    """ Represents an HL7 MLLP channel.
    """
    needs_self_client = False
    wrapper_type = 'HL7 MLLP channel'
    build_if_not_active = True

    def __init__(self, *args, **kwargs):
        super(ChannelHL7MLLPWrapper, self).__init__(*args, **kwargs)
        self._impl = None

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            logger.warn('QQQ _init_impl %s', self)

            # We can assume we are done building the channel now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        logger.warn('QQQ _delete %s', self)

# ################################################################################################################################

    def _ping(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
