# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import FILE_TRANSFER
from zato.server.service import Service

# ################################################################################################################################

class ChannelFileTransferHandler(Service):
    """ A no-op marker service uses by file transfer channels.
    """
    name = FILE_TRANSFER.SCHEDULER_SERVICE

    def handle(self):
        self.logger.warn('ZZZ `%s`', self.request.raw_request)
        pass

# ################################################################################################################################
