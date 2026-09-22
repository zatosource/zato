# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services every queue delivery suite copies into its server's pickup directory - the ones that know nothing
# of the type under test. Where a connection has to be looked up, they ask the type's own get-connection service,
# which every suite provides under the same name and which answers with the connection's id and type.

# stdlib
from json import loads

# Zato
from zato.common.pubsub.dlq import get_dlq_sub_key, get_dlq_topic_name
from zato.common.pubsub.outgoing import get_outgoing_sub_key, get_outgoing_topic_name
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

_get_connection_service = 'test.queue-delivery.get-connection'

# ################################################################################################################################
# ################################################################################################################################

def _get_connection(service:'Service', conn_name:'str') -> 'anydict':
    """ What the type's own service knows about a connection.
    """
    out = service.invoke(_get_connection_service, {'conn_name': conn_name})
    return out

# ################################################################################################################################

def _browse(service:'Service', topic_name:'str', sub_key:'str', document_key:'str') -> 'anylist':
    """ Every pending message of a sub key on a topic, oldest first, each with its document under the given key.
    """
    messages, _ = service.server.pubsub_backend.browse_messages(topic_name, sub_key, 'pending', needs_data=True)

    out:'anylist' = []

    for message in messages:
        out.append({
            'msg_id': message['msg_id'],
            document_key: loads(message['data']),
        })

    return out

# ################################################################################################################################
# ################################################################################################################################

class GetPubSubBackend(Service):
    """ Answers with what database the server's own pub/sub backend runs on.
    """

    name = 'test.queue-delivery.get-pubsub-backend'

    def handle(self) -> 'None':

        url = self.server.pubsub_backend.engine.url

        # Oracle DB is addressed by a service name in the query string, not by a database in the path
        name = url.database

        if not name:
            name = url.query['service_name']

        self.response.payload = {
            'type': url.get_backend_name(),
            'name': name,
        }

# ################################################################################################################################
# ################################################################################################################################

class GetQueue(Service):
    """ Answers with what the server knows about the queue of one outgoing connection.
    """

    name = 'test.queue-delivery.get-queue'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        connection = _get_connection(self, conn_name)
        conn_type = connection['conn_type']
        conn_id = connection['id']

        sub_key = get_outgoing_sub_key(conn_type, conn_id)
        topic_name = get_outgoing_topic_name(conn_type, conn_name)

        depth = self.server.config_manager.outgoing_queue_depth.get(sub_key)

        self.response.payload = {
            'conn_id': conn_id,
            'sub_key': sub_key,
            'topic_name': topic_name,
            'depth': depth,
            'messages': _browse(self, topic_name, sub_key, 'envelope'),
        }

# ################################################################################################################################
# ################################################################################################################################

class GetDLQ(Service):
    """ Answers with what the DLQ of one outgoing connection holds, oldest first.
    """

    name = 'test.queue-delivery.get-dlq'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        connection = _get_connection(self, conn_name)
        conn_type = connection['conn_type']
        conn_id = connection['id']

        sub_key = get_dlq_sub_key(conn_type, conn_id)
        topic_name = get_dlq_topic_name(conn_type, conn_name)

        self.response.payload = {
            'sub_key': sub_key,
            'topic_name': topic_name,
            'messages': _browse(self, topic_name, sub_key, 'document'),
        }

# ################################################################################################################################
# ################################################################################################################################

class SubscribeTopic(Service):
    """ Subscribes a test sub key to a topic.
    """

    name = 'test.queue-delivery.subscribe-topic'

    def handle(self) -> 'None':

        topic_name = self.request.raw_request['topic_name']
        sub_key = self.request.raw_request['sub_key']

        self.server.pubsub_backend.subscribe(sub_key, topic_name)

        self.response.payload = {'sub_key': sub_key}

# ################################################################################################################################
# ################################################################################################################################

class GetTopicMessages(Service):
    """ Answers with the messages waiting for a test sub key on a topic, oldest first, and takes them off the topic.
    """

    name = 'test.queue-delivery.get-topic-messages'

    def handle(self) -> 'None':

        topic_name = self.request.raw_request['topic_name']
        sub_key = self.request.raw_request['sub_key']

        messages = _browse(self, topic_name, sub_key, 'document')

        for message in messages:
            _ = self.server.pubsub_backend.ack_message(sub_key, message['msg_id'])

        self.response.payload = {'messages': messages}

# ################################################################################################################################
# ################################################################################################################################

class GetTopicSubscribers(Service):
    """ Answers with the sub keys the pub/sub database has under a topic.
    """

    name = 'test.queue-delivery.get-topic-subscribers'

    def handle(self) -> 'None':

        topic_name = self.request.raw_request['topic_name']

        sub_key_list = self.server.pubsub_backend.get_topic_subscribers(topic_name)

        self.response.payload = {'sub_key_list': sub_key_list}

# ################################################################################################################################
# ################################################################################################################################

class InvokeService(Service):
    """ Invokes any service by name with a request dict.
    """

    name = 'test.queue-delivery.invoke'

    def handle(self) -> 'None':

        service_name = self.request.raw_request['service_name']
        request = self.request.raw_request['request']

        response = self.invoke(service_name, request)

        self.response.payload = {'response': response}

# ################################################################################################################################
# ################################################################################################################################
