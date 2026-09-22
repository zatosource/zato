# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services of the outgoing SOAP suite - what is SOAP's own of the contract every type's suite fulfils.

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.outgoing import OutgoingType, SendResult
from zato.common.soap.common import SOAPFault
from zato.common.soap.message import SOAPMessage
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_connection = 'outgoing'
_transport = 'soap'

# The operation every send invokes - the same name the suite's type spells out
_operation = 'ProcessOrder'

# The opaque attributes, which an edit that leaves them out would clear
_opaque_fields = ('is_audit_log_active', 'validate_tls', 'content_type', 'use_ws_addressing', 'use_mtom', \
    'tls_client_cert', 'tls_client_key', 'body_credentials') + HTTP_SOAP.Invocation.FieldList + \
    HTTP_SOAP.HealthCheck.FieldList + HTTP_SOAP.Retry.FieldList + HTTP_SOAP.Queue.FieldList + HTTP_SOAP.DLQ.FieldList

_own_fields = (
    'id', 'name', 'host', 'url_path', 'soap_action', 'soap_version', 'timeout', 'ping_method', 'pool_size',
    'is_active', 'security_id',
)

# ################################################################################################################################
# ################################################################################################################################

def _message_from(data:'anydict') -> 'SOAPMessage':
    """ A flat document as the message an operation is invoked with.
    """
    out = SOAPMessage()

    for name, value in data.items():
        setattr(out, name, value)

    return out

# ################################################################################################################################

def _response_to_dict(response:'any_') -> 'anydictnone':
    """ What the endpoint answered, as a dict - a response message or the fault it turned the invocation down with.
    """
    if response is None:
        out = None
    else:
        out = {
            'is_fault': isinstance(response, SOAPFault),
            'text': str(response),
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
            'is_ok': True,
            'response': _response_to_dict(result),
        }

    return out

# ################################################################################################################################

def _send_one(service:'Service', conn_name:'str', data:'any_') -> 'stranydict':
    """ One send through a connection - with the switch off, a fault is the endpoint's answer, not something raised.
    """
    message = _message_from(data)

    try:
        result = service.soap[conn_name].invoke(_operation, message)
        out = _result_to_dict(result)
        out['raised'] = ''

    except SOAPFault as fault:
        out = {
            'is_send_result': False,
            'is_ok': False,
            'response': _response_to_dict(fault),
            'raised': '',
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
    """ Invokes an operation once through an outgoing SOAP connection.
    """

    name = 'test.queue-delivery.send'

    def handle(self) -> 'None':

        raw_request = self.request.raw_request

        conn_name = raw_request['conn_name']
        data = raw_request['data']

        # The headers of a send are HTTP's own - a SOAP connection's headers come from its configuration
        self.response.payload = _send_one(self, conn_name, data)

# ################################################################################################################################
# ################################################################################################################################

class SendMany(Service):
    """ Invokes an operation through one connection once per document, in this order.
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
    """ Pings through an outgoing SOAP connection - a read that is never a delivery.
    """

    name = 'test.queue-delivery.read'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        response = self.soap[conn_name].conn.ping(self.cid, return_response=True)

        out = {
            'is_send_result': False,
            'is_ok': response.ok,
            'response': {
                'status_code': response.status_code,
                'text': response.text,
            },
            'cid': self.cid,
        }

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class GetConnection(Service):
    """ Answers with the configuration an outgoing SOAP connection has right now.
    """

    name = 'test.queue-delivery.get-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        item = self.server.config_manager.config_store.out_soap[conn_name]
        config = item['config']

        out:'stranydict' = {
            'conn_type': OutgoingType.SOAP,
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
    """ Changes some fields of an outgoing SOAP connection as the Dashboard does.
    """

    name = 'test.queue-delivery.edit-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        changes = self.request.raw_request['changes']

        item = self.server.config_manager.config_store.out_soap[conn_name]
        config = item['config']

        request = _build_create_edit_request(config, changes)

        _ = self.invoke('zato.http-soap.edit', request)

        self.response.payload = {'id': config['id']}

# ################################################################################################################################
# ################################################################################################################################

class CreateConnection(Service):
    """ Creates an outgoing SOAP connection configured like an existing one, under a new name, as the Dashboard does.
    """

    name = 'test.queue-delivery.create-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        like_conn_name = self.request.raw_request['like_conn_name']

        item = self.server.config_manager.config_store.out_soap[like_conn_name]
        config = item['config']

        request = _build_create_edit_request(config, {'name': conn_name, 'is_internal': False})
        _ = request.pop('id')

        response = self.invoke('zato.http-soap.create', request)

        self.response.payload = {'id': response['id']}

# ################################################################################################################################
# ################################################################################################################################

class DeleteConnection(Service):
    """ Deletes an outgoing SOAP connection as the Dashboard does.
    """

    name = 'test.queue-delivery.delete-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        item = self.server.config_manager.config_store.out_soap[conn_name]
        conn_id = item['config']['id']

        _ = self.invoke('zato.http-soap.delete', {'id': conn_id})

        self.response.payload = {'id': conn_id}

# ################################################################################################################################
# ################################################################################################################################
