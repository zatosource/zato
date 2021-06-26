# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import FILE_TRANSFER
from zato.common.util.file_transfer import parse_extra_into_list
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class ChannelFileTransferHandler(Service):
    """ A no-op marker service uses by file transfer channels.
    """
    name = FILE_TRANSFER.SCHEDULER_SERVICE

# ################################################################################################################################

    def handle(self):

        extra = self.request.raw_request

        if not extra:
            return

        # Convert input parameters into a list of channel (observer) IDs ..
        extra = parse_extra_into_list(extra)

        # .. and run each observer in a new greenlet.
        for channel_id in extra:
            self.server.worker_store.file_transfer_api.run_snapshot_observer(channel_id, 1)

# ################################################################################################################################
# ################################################################################################################################
