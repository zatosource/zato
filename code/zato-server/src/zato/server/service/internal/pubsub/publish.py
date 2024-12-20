# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import AsIs, Int, List
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anytuple
    anytuple = anytuple

# ################################################################################################################################
# ################################################################################################################################

class Publish(AdminService):
    """ Actual implementation of message publishing exposed through other services to the outside world.
    """
    call_hooks = False

    class SimpleIO:
        input_required = ('topic_name',)
        input_optional = (AsIs('data'), List('data_list'), AsIs('msg_id'), Int('priority'), Int('expiration'),
            'mime_type', AsIs('correl_id'), 'in_reply_to', AsIs('ext_client_id'), 'ext_pub_time', 'pub_pattern_matched',
            'endpoint_id', 'endpoint_name', 'security_id', 'security_name', 'ws_channel_id', 'data_parsed', AsIs('group_id'),
            Int('position_in_group'), List('reply_to_sk'), List('deliver_to_sk'), 'user_ctx', AsIs('zato_ctx'),
            AsIs('has_gd')) # type: anytuple
        output_optional = (AsIs('msg_id'), List('msg_id_list')) # type: anytuple

# ################################################################################################################################

    def handle(self):

        # Run the publication based on our input  ..
        response = self.pubsub.impl_publisher.run_from_dict(self.cid, self.request.input)

        # .. and assign the response to our return data, assuming that there is anything to return.
        if response:
            if isinstance(response, str):
                self.response.payload.msg_id = response
            else:
                self.response.payload.msg_id_list = response

# ################################################################################################################################
