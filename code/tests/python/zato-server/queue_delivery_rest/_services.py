# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services of the outgoing REST suite - what is REST's own of the contract every type's suite fulfils.

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.outgoing import OutgoingType, SendResult
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

class GetConnection(Service):
    """ Answers with the configuration an outgoing REST connection has right now.
    """

    name = 'test.queue-delivery.get-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        item = self.server.config_manager.config_store.out_plain_http[conn_name]
        config = item['config']

        out:'stranydict' = {
            'conn_type': OutgoingType.REST,
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
    out = {
        'connection': _connection,
        'transport': _transport,
    }

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
    """ Changes some fields of an outgoing REST connection as the Dashboard does.
    """

    name = 'test.queue-delivery.edit-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        changes = self.request.raw_request['changes']

        item = self.server.config_manager.config_store.out_plain_http[conn_name]
        config = item['config']

        request = _build_create_edit_request(config, changes)

        _ = self.invoke('zato.http-soap.edit', request)

        self.response.payload = {'id': config['id']}

# ################################################################################################################################
# ################################################################################################################################

class CreateConnection(Service):
    """ Creates an outgoing REST connection configured like an existing one, under a new name, as the Dashboard does.
    """

    name = 'test.queue-delivery.create-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        like_conn_name = self.request.raw_request['like_conn_name']

        item = self.server.config_manager.config_store.out_plain_http[like_conn_name]
        config = item['config']

        request = _build_create_edit_request(config, {'name': conn_name})
        _ = request.pop('id')

        response = self.invoke('zato.http-soap.create', request)

        self.response.payload = {'id': response['id']}

# ################################################################################################################################
# ################################################################################################################################

class DeleteConnection(Service):
    """ Deletes an outgoing REST connection as the Dashboard does.
    """

    name = 'test.queue-delivery.delete-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        item = self.server.config_manager.config_store.out_plain_http[conn_name]
        conn_id = item['config']['id']

        _ = self.invoke('zato.http-soap.delete', {'id': conn_id})

        self.response.payload = {'id': conn_id}

# ################################################################################################################################
# ################################################################################################################################
