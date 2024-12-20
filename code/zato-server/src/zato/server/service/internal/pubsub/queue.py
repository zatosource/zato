# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.query.pubsub.queue import acknowledge_delivery, get_messages, get_queue_depth_by_sub_key
from zato.common.util.time_ import datetime_from_ms, utcnow_as_ms
from zato.server.service import AsIs, Dict, List
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anytuple
    anytuple = anytuple

# ################################################################################################################################
# ################################################################################################################################

_batch_size=PUBSUB.DEFAULT.GET_BATCH_SIZE

# ################################################################################################################################
# ################################################################################################################################

class GetMessages(AdminService):
    """ Returns a list of messages available for a given sub_key.
    Returns up to batch_size messages, if batch_size is not given, it is equal to 100.
    """
    class SimpleIO(AdminSIO):
        input_required = 'sub_key'
        input_optional = 'batch_size'
        output_optional = AsIs('msg_id'), AsIs('correl_id'), 'in_reply_to', 'priority', 'size', \
            'data_format', 'mime_type', 'data', 'expiration', 'expiration_time', 'ext_client_id', 'topic_name', \
            'recv_time', 'delivery_count' # type: anytuple
        output_repeated = True

    def handle(self) -> 'None':
        input = self.request.input
        batch_size = input.batch_size or _batch_size

        with closing(self.odb.session()) as session:
            msg_list = get_messages(session, self.server.cluster_id, input.sub_key, batch_size, utcnow_as_ms())

            for elem in msg_list:
                ext_pub_time = datetime_from_ms(elem.ext_pub_time) if elem.ext_pub_time else None

                self.response.payload.append({
                    'msg_id': elem.msg_id,
                    'correl_id': elem.correl_id,
                    'in_reply_to': elem.in_reply_to,
                    'priority': elem.priority,
                    'size': elem.size,
                    'data_format': elem.data_format,
                    'mime_type': elem.mime_type,
                    'data': elem.data,
                    'expiration': elem.expiration,
                    'expiration_time': datetime_from_ms(elem.expiration_time),
                    'ext_client_id': elem.ext_client_id,
                    'ext_pub_time': ext_pub_time,
                    'topic_name': elem.topic_name,
                    'recv_time': datetime_from_ms(elem.recv_time),
                    'delivery_count': elem.delivery_count,
                })

            # We need to commit the session because the underlying query issued SELECT FOR UPDATE
            session.commit()

# ################################################################################################################################

class AcknowledgeDelivery(AdminService):
    """ Invoked by API clients to confirm that delivery of all messages from input msg_id_list was successful.
    """
    class SimpleIO(AdminSIO):
        input_required = 'sub_key', List('msg_id_list') # type: anytuple

    def handle(self) -> 'None':

        sub_key = self.request.input.sub_key
        msg_id_list = self.request.input.msg_id_list

        if msg_id_list:
            with closing(self.odb.session()) as session:

                # Call SQL UPDATE ..
                acknowledge_delivery(session, self.server.cluster_id, sub_key, msg_id_list, utcnow_as_ms())

                # .. and confirm the transaction
                session.commit()

# ################################################################################################################################

class GetQueueDepthBySubKey(AdminService):
    """ For each sub_key given on input, return depth of its associated message queue.
    """
    class SimpleIO(AdminSIO):
        input_optional = 'sub_key', List('sub_key_list') # type: anytuple
        output_optional = Dict('queue_depth'),           # type: anytuple

    def handle(self) -> 'None':
        input = self.request.input
        input.require_any('sub_key', 'sub_key_list')

        # Support both on input but always pass on a list further on
        sub_key_list = [input.sub_key] if input.sub_key else input.sub_key_list

        # Response to return
        response = {}

        with closing(self.odb.session()) as session:
            for item in sub_key_list:
                response[item] = get_queue_depth_by_sub_key(session, self.server.cluster_id, item, utcnow_as_ms())

        self.response.payload.queue_depth = response

# ################################################################################################################################
