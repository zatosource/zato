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

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import FILE_TRANSFER
from zato.common.util.file_transfer import parse_extra_into_list
from zato.common.util.api import spawn_greenlet
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class ChannelFileTransferHandler(Service):
    """ A no-op marker service uses by file transfer channels.
    """
    name = FILE_TRANSFER.SCHEDULER_SERVICE

# ################################################################################################################################

    def run_observer(self, channel_id):
        # type: (int) -> None

        channel = self.server.worker_store.file_transfer_api.observer_dict

        self.logger.warn('ZZZ-2 `%s`', channel)

# ################################################################################################################################

    def handle(self):

        extra = '16;'#; 17' #self.request.raw_request

        # Convert input parameters into a list of channel (observer) IDs ..
        extra = parse_extra_into_list(extra)

        # .. and run each observer in a new greenlet.
        for channel_id in extra:
            spawn_greenlet(self.run_observer, channel_id)

# ################################################################################################################################
# ################################################################################################################################
'''
