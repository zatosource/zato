# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common import PUB_SUB
from zato.common.pubsub import Message
from zato.server.service import AsIs, Int, UTC
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of mesages from a topic or consumer queue.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_message_get_list_request'
        response_elem = 'zato_pubsub_message_get_list_response'
        input_required = ('cluster_id', 'source_type', 'source_name')
        output_required = (AsIs('msg_id'), 'topic', 'mime_type', Int('priority'), Int('expiration'),
            UTC('creation_time_utc'), UTC('expire_at_utc'), 'producer')

    def get_data(self):
        if self.request.input.source_type == PUB_SUB.MESSAGE_SOURCE.TOPIC.id:
            func = 'get_topic_message_list'
        else:
            func = 'get_consumer_queue_message_list'

        func = getattr(self.pubsub, func)

        for item in func(self.request.input.source_name):
            yield item.to_dict()

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################

class Details(AdminService):
    """ Returns basic information regarding a message from a topic or a consumer queue.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_message_get_info_request'
        response_elem = 'zato_pubsub_message_get_info_response'
        input_required = ('cluster_id', 'name')
        output_required = (Int('current_depth'), Int('consumers_count'), Int('producers_count'), UTC('last_pub_time'))

    def handle(self):
        self.response.payload.current_depth = self.pubsub.get_topic_depth(self.request.input.name)
        self.response.payload.consumers_count = self.pubsub.get_consumers_count(self.request.input.name)
        self.response.payload.producers_count = self.pubsub.get_producers_count(self.request.input.name)
        self.response.payload.last_pub_time = self.pubsub.get_last_pub_time(self.request.input.name)

# ################################################################################################################################

class Delete(AdminService):
    """ Irrevocably deletes a message from a producer's topic or a consumer's queue.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_message_delete_request'
        response_elem = 'zato_pubsub_message_delete_response'
        input_required = (AsIs('msg_id'), 'name', 'source_type')

    def handle(self):

        if self.request.input.source_type == PUB_SUB.MESSAGE_SOURCE.TOPIC.id:
            func = 'delete_from_topic'
        else:
            func = 'delete_from_consumer_queue'

        getattr(self.pubsub, func)(self.request.input.name, self.request.input.msg_id)

# ################################################################################################################################
