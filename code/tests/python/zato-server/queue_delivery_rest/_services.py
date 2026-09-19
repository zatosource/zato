# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.dlq import get_dlq_sub_key, get_dlq_topic_name
from zato.common.pubsub.outgoing import get_outgoing_sub_key, get_outgoing_topic_name, OutgoingType, SendResult
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydictnone, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_connection = 'outgoing'
_transport = 'plain_http'

# The opaque attributes, which an edit that leaves them out would clear
_opaque_fields = ('is_audit_log_active',) + HTTP_SOAP.Invocation.FieldList + HTTP_SOAP.HealthCheck.FieldList + \
    HTTP_SOAP.Retry.FieldList + HTTP_SOAP.Queue.FieldList + HTTP_SOAP.DLQ.FieldList

_own_fields = (
    'id', 'name', 'host', 'url_path', 'method', 'data_format', 'timeout', 'ping_method', 'pool_size',
    'is_active', 'security_id',
)

# ################################################################################################################################
# ################################################################################################################################

def _response_to_dict(response:'any_') -> 'anydictnone':
    """ What the endpoint answered, as a dict.
    """
    if response is None:
        out = None
    else:
        out = {
            'status_code': response.status_code,
            'text': response.text,
        }

    return out

# ################################################################################################################################

def _result_to_dict(result:'any_') -> 'stranydict':
    """ What one send came back with, as a dict.
    """
    if isinstance(result, SendResult):
        out = {
            'is_send_result': True,
            'is_ok': result.is_ok,
            'is_in_queue': result.is_in_queue,
            'msg_id': result.msg_id,
            'error': result.error,
            'response': _response_to_dict(result.response),
        }
    else:
        out = {
            'is_send_result': False,
            'is_ok': result.ok,
            'response': _response_to_dict(result),
        }

    return out

# ################################################################################################################################

def _send_one(service:'Service', conn_name:'str', data:'any_', headers:'any_') -> 'stranydict':
    """ One send through a connection.
    """
    try:
        result = service.rest[conn_name].post(data, headers=headers)
        out = _result_to_dict(result)
        out['raised'] = ''

    except Exception as e:
        out = {
            'raised': e.__class__.__name__,
            'error': str(e),
        }

    out['cid'] = service.cid
    return out

# ################################################################################################################################
# ################################################################################################################################

class Send(Service):
    """ Sends one message through an outgoing REST connection.
    """

    name = 'test.queue-delivery.send'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        data = self.request.raw_request['data']
        headers = self.request.raw_request['headers']

        self.response.payload = _send_one(self, conn_name, data, headers)

# ################################################################################################################################
# ################################################################################################################################

class SendMany(Service):
    """ Sends messages through one connection one after another, in this order.
    """

    name = 'test.queue-delivery.send-many'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        data_list = self.request.raw_request['data_list']

        results:'anylist' = []

        for data in data_list:
            results.append(_send_one(self, conn_name, data, {}))

        self.response.payload = {'results': results}

# ################################################################################################################################
# ################################################################################################################################

class Read(Service):
    """ Reads through an outgoing REST connection.
    """

    name = 'test.queue-delivery.read'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        result = self.rest[conn_name].get()

        out = _result_to_dict(result)
        out['cid'] = self.cid

        self.response.payload = out

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
    """ Answers with what the server knows about the queue of one outgoing REST connection.
    """

    name = 'test.queue-delivery.get-queue'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        item = self.server.config_manager.config_store.out_plain_http[conn_name]
        conn_id = item['config']['id']

        sub_key = get_outgoing_sub_key(OutgoingType.REST, conn_id)
        topic_name = get_outgoing_topic_name(OutgoingType.REST, conn_name)

        depth = self.server.config_manager.outgoing_queue_depth.get(sub_key)

        messages, _ = self.server.pubsub_backend.browse_messages(topic_name, sub_key, 'pending', needs_data=True)

        out_messages:'anylist' = []

        for message in messages:
            out_messages.append({
                'msg_id': message['msg_id'],
                'envelope': loads(message['data']),
            })

        self.response.payload = {
            'sub_key': sub_key,
            'topic_name': topic_name,
            'depth': depth,
            'messages': out_messages,
        }

# ################################################################################################################################
# ################################################################################################################################

class GetDLQ(Service):
    """ Answers with what the DLQ of one outgoing REST connection holds, oldest first.
    """

    name = 'test.queue-delivery.get-dlq'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        item = self.server.config_manager.config_store.out_plain_http[conn_name]
        conn_id = item['config']['id']

        sub_key = get_dlq_sub_key(OutgoingType.REST, conn_id)
        topic_name = get_dlq_topic_name(OutgoingType.REST, conn_name)

        messages, _ = self.server.pubsub_backend.browse_messages(topic_name, sub_key, 'pending', needs_data=True)

        out_messages:'anylist' = []

        for message in messages:
            out_messages.append({
                'msg_id': message['msg_id'],
                'document': loads(message['data']),
            })

        self.response.payload = {
            'sub_key': sub_key,
            'topic_name': topic_name,
            'messages': out_messages,
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
    """ Answers with the messages waiting for a test sub key on a topic, oldest first.
    """

    name = 'test.queue-delivery.get-topic-messages'

    def handle(self) -> 'None':

        topic_name = self.request.raw_request['topic_name']
        sub_key = self.request.raw_request['sub_key']

        messages, _ = self.server.pubsub_backend.browse_messages(topic_name, sub_key, 'pending', needs_data=True)

        out_messages:'anylist' = []

        for message in messages:
            out_messages.append({
                'msg_id': message['msg_id'],
                'document': loads(message['data']),
            })
            _ = self.server.pubsub_backend.ack_message(sub_key, message['msg_id'])

        self.response.payload = {'messages': out_messages}

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

class GetConnection(Service):
    """ Answers with the configuration an outgoing REST connection has right now.
    """

    name = 'test.queue-delivery.get-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        item = self.server.config_manager.config_store.out_plain_http[conn_name]
        config = item['config']

        out:'stranydict' = {}

        for field_name in _own_fields:
            out[field_name] = config[field_name]

        for field_name in _opaque_fields:
            if field_name in config:
                out[field_name] = config[field_name]

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class EditConnection(Service):
    """ Changes some fields of an outgoing REST connection as the Dashboard does.
    """

    name = 'test.queue-delivery.edit-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        changes = self.request.raw_request['changes']

        item = self.server.config_manager.config_store.out_plain_http[conn_name]
        config = item['config']

        request = {
            'connection': _connection,
            'transport': _transport,
        }

        for field_name in _own_fields:
            request[field_name] = config[field_name]

        for field_name in _opaque_fields:
            if field_name in config:
                request[field_name] = config[field_name]

        request.update(changes)

        _ = self.invoke('zato.http-soap.edit', request)

        self.response.payload = {'id': config['id']}

# ################################################################################################################################
# ################################################################################################################################
