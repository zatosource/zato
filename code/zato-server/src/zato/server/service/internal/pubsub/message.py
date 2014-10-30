# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import PUB_SUB
from zato.server.service import AsIs, Int, UTC
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class _SourceTypeAware(AdminService):
    ZATO_DONT_DEPLOY = True

    source_type_func = {
        'get_list': {
            PUB_SUB.MESSAGE_SOURCE.TOPIC.id: 'get_topic_message_list',
            PUB_SUB.MESSAGE_SOURCE.CONSUMER_QUEUE.id: 'get_consumer_queue_message_list',
        },
        'delete': {
            PUB_SUB.MESSAGE_SOURCE.TOPIC.id: 'delete_from_topic',
            PUB_SUB.MESSAGE_SOURCE.CONSUMER_QUEUE.id: 'delete_from_consumer_queue',
        },
    }

    def get_pubsub_api_func(self, action, source_type):
        return getattr(self.pubsub, self.source_type_func[action][source_type])

class GetList(_SourceTypeAware):
    """ Returns a list of mesages from a topic or consumer queue.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_message_get_list_request'
        response_elem = 'zato_pubsub_message_get_list_response'
        input_required = ('cluster_id', 'source_type', 'source_name')
        output_required = (AsIs('msg_id'), 'topic', 'mime_type', Int('priority'), Int('expiration'),
            UTC('creation_time_utc'), UTC('expire_at_utc'), 'producer')

    def get_data(self):
        func = self.get_pubsub_api_func('get_list', self.request.input.source_type)
        for item in func(self.request.input.source_name):
            yield item.to_dict()

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################

class Get(_SourceTypeAware):
    """ Returns basic information regarding a message from a topic or a consumer queue.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_message_get_request'
        response_elem = 'zato_pubsub_message_get_response'
        input_required = ('cluster_id', AsIs('msg_id'))
        output_required = ('topic', 'producer', 'priority', 'mime_type', 'expiration',
            UTC('creation_time_utc'), UTC('expire_at_utc'))
        output_optional = ('payload',)

    def handle(self):
        self.response.payload = self.pubsub.get_message(self.request.input.msg_id)

# ################################################################################################################################

class Delete(_SourceTypeAware):
    """ Irrevocably deletes a message from a producer's topic or a consumer's queue.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_message_delete_request'
        response_elem = 'zato_pubsub_message_delete_response'
        input_required = ('cluster_id', AsIs('msg_id'), 'source_name', 'source_type')

    def handle(self):
        func = self.get_pubsub_api_func('delete', self.request.input.source_type)
        func(self.request.input.source_name, self.request.input.msg_id)

# ################################################################################################################################
