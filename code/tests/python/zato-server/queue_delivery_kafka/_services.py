# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services of the outgoing Kafka suite - what is Kafka's own of the contract every type's suite fulfils.
# A document travels as JSON in the value of a record, and what Kafka answers a message with is the record's error.

# stdlib
from json import dumps

# Zato
from zato.common.pubsub.delivery import DeliveryExhausted
from zato.common.pubsub.outgoing import OutgoingType, SendRejected, SendResult
from zato.server.generic.api.outconn_kafka import outconn_config_defaults
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The columns of a generic connection an edit sends back as they are
_own_fields = ('id', 'name', 'type_', 'address', 'pool_size', 'is_active', 'is_internal', 'is_channel', 'is_outconn')

# The opaque attributes, which an edit that leaves them out would clear
_opaque_fields = tuple(outconn_config_defaults) + ('security_id', 'security_name', 'auth_type', 'is_audit_log_active')

# ################################################################################################################################
# ################################################################################################################################

def _answer_to_dict(answer:'any_') -> 'anydictnone':
    """ What Kafka answered a message with, as a dict - where it landed, or the error it was turned down with.
    """
    if answer is None:
        out = None

    elif hasattr(answer, 'offset'):
        out = {
            'topic': answer.topic,
            'partition': answer.partition,
            'offset': answer.offset,
        }

    else:
        out = {'text': str(answer)}

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
            'response': _answer_to_dict(result.response),
        }
    else:
        out = {
            'is_send_result': False,
            'is_ok': True,
            'response': _answer_to_dict(result),
        }

    return out

# ################################################################################################################################

def _kafka_answer_of(e:'Exception') -> 'any_':
    """ What Kafka answered when a direct send with the switch off ran out of attempts, None when nothing answered -
    the rejection the last attempt raised keeps the answer, if there was one.
    """
    cause = e.__cause__

    if isinstance(cause, SendRejected):
        return cause.response

    return None

# ################################################################################################################################

def _send_one(service:'Service', conn_name:'str', data:'anydict', headers:'anydict | None'=None) -> 'stranydict':
    """ One send through a connection - with the switch off, a message Kafka turned down is Kafka's answer, not
    something raised, and a send that got no answer at all raises.
    """
    try:
        result = service.out.kafka[conn_name].send(dumps(data), headers=headers)
        out = _result_to_dict(result)
        out['raised'] = ''

    except DeliveryExhausted as e:

        if (answer := _kafka_answer_of(e)) is not None:
            out = {
                'is_send_result': False,
                'is_ok': False,
                'response': _answer_to_dict(answer),
                'raised': '',
                'error': e.error,
            }
        else:
            out = {
                'raised': e.__class__.__name__,
                'error': e.error,
            }

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
    """ Sends one message through an outgoing Kafka connection.
    """

    name = 'test.queue-delivery.send'

    def handle(self) -> 'None':

        raw_request = self.request.raw_request

        conn_name = raw_request['conn_name']
        data = raw_request['data']
        headers = raw_request.get('headers') or None

        self.response.payload = _send_one(self, conn_name, data, headers)

# ################################################################################################################################
# ################################################################################################################################

class SendMany(Service):
    """ Sends messages through one connection once per document, in this order.
    """

    name = 'test.queue-delivery.send-many'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        data_list = self.request.raw_request['data_list']

        results:'anylist' = []

        for data in data_list:
            results.append(_send_one(self, conn_name, data))

        self.response.payload = {'results': results}

# ################################################################################################################################
# ################################################################################################################################

class Read(Service):
    """ Pings an outgoing Kafka connection - a look at the metadata of its instances, which is never a delivery.
    """

    name = 'test.queue-delivery.read'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        # Our response to produce
        out:'anydict'

        try:
            self.out.kafka[conn_name].ping()
            out = {
                'is_send_result': False,
                'is_ok': True,
                'response': None,
            }

        except Exception as e:
            out = {
                'is_send_result': False,
                'is_ok': False,
                'response': {'text': str(e)},
            }

        out['cid'] = self.cid

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

def _get_config(service:'Service', conn_name:'str') -> 'stranydict':
    """ The configuration an outgoing Kafka connection has right now.
    """
    out = service.server.config_manager.outconn_kafka[conn_name]
    return out

# ################################################################################################################################
# ################################################################################################################################

class GetConnection(Service):
    """ Answers with the configuration an outgoing Kafka connection has right now.
    """

    name = 'test.queue-delivery.get-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        config = _get_config(self, conn_name)

        out:'stranydict' = {
            'conn_type': OutgoingType.KAFKA,
        }

        for field_name in _own_fields:
            out[field_name] = config[field_name]

        for field_name in _opaque_fields:
            if field_name in config:
                out[field_name] = config[field_name]

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

def _build_create_edit_request(config:'stranydict', changes:'stranydict') -> 'stranydict':
    """ A create or edit request out of a connection's configuration with some fields changed.
    """
    out = {}

    for field_name in _own_fields:
        out[field_name] = config[field_name]

    for field_name in _opaque_fields:
        if field_name in config:
            out[field_name] = config[field_name]

    out.update(changes)

    return out

# ################################################################################################################################
# ################################################################################################################################

class EditConnection(Service):
    """ Changes some fields of an outgoing Kafka connection as the Dashboard does.
    """

    name = 'test.queue-delivery.edit-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        changes = self.request.raw_request['changes']

        config = _get_config(self, conn_name)

        request = _build_create_edit_request(config, changes)

        _ = self.invoke('zato.generic.connection.edit', request)

        self.response.payload = {'id': config['id']}

# ################################################################################################################################
# ################################################################################################################################

class CreateConnection(Service):
    """ Creates an outgoing Kafka connection configured like an existing one, under a new name, as the Dashboard does.
    """

    name = 'test.queue-delivery.create-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        like_conn_name = self.request.raw_request['like_conn_name']

        config = _get_config(self, like_conn_name)

        request = _build_create_edit_request(config, {'name': conn_name})
        _ = request.pop('id')

        response = self.invoke('zato.generic.connection.create', request)

        self.response.payload = {'id': response['id']}

# ################################################################################################################################
# ################################################################################################################################

class DeleteConnection(Service):
    """ Deletes an outgoing Kafka connection as the Dashboard does.
    """

    name = 'test.queue-delivery.delete-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        config = _get_config(self, conn_name)
        conn_id = config['id']

        _ = self.invoke('zato.generic.connection.delete', {'id': conn_id})

        self.response.payload = {'id': conn_id}

# ################################################################################################################################
# ################################################################################################################################
