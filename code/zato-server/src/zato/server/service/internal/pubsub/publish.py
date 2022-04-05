# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from zato.server.pubsub.publisher import Publisher, PubRequest
from zato.server.service import AsIs, Int, List
from zato.server.service.internal import AdminService

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
            'security_id', 'ws_channel_id', 'data_parsed', AsIs('group_id'),
            Int('position_in_group'), 'endpoint_id', List('reply_to_sk'), List('deliver_to_sk'), 'user_ctx', AsIs('zato_ctx'),
            AsIs('has_gd'))
        output_optional = (AsIs('msg_id'), List('msg_id_list'))

# ################################################################################################################################

    def handle(self):

        # Prepare a publisher object that will handle the publication ..
        publisher = Publisher(
            cid = self.cid,
            pubsub = self.pubsub,
            server = self.server,
            service_invoke_func = self.invoke,
            new_session_func = self.odb.session
        )

        # .. prepare the request for the publisher ..
        request = PubRequest._zato_from_dict(self.request.input)

        # .. run the publication  ..
        response = publisher.run(request)

        # .. and assign the output to our response, assuming that there was any ..
        if response:
            if isinstance(response, str):
                self.response.payload.msg_id = response
            else:
                self.response.payload.msg_id_list = response

# ################################################################################################################################
