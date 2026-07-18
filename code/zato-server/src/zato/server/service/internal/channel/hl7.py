# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.json_internal import dumps
from zato.server.generic.api.channel_hl7_mllp import get_current_state
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

class GetCurrentState(AdminService):
    """ Returns the live state of HL7 MLLP channels - the in-process counters
    the channel dashboard reads: received, acked, nacked, errored, the NACK streak,
    last-message time and the listener's condition. Counters come straight
    from the message path, never from the audit database.
    """
    name = 'zato.channel.hl7.get-current-state'
    input = '-name'
    output = 'response_data'

    def handle(self) -> 'None':

        channels = get_current_state()

        # An optional name narrows the response to one channel
        name = self.request.input.name
        if name:
            channels = [item for item in channels if item['name'] == name]

        response = {
            'channels': channels,
            'cid': self.cid,
        }

        self.response.payload.response_data = dumps(response)

# ################################################################################################################################
# ################################################################################################################################
