# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services of the outgoing FHIR suite - what is FHIR's own of the contract every type's suite fulfils.

# fhirpy
from fhirpy.base.exceptions import BaseFHIRError

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.outgoing import OutgoingType, SendResult
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The resource type every send creates - the same one the suite's type spells out
_resource_type = 'Patient'

# The resource a read asks for
_read_resource_id = 'read-1'

# The opaque attributes, which an edit that leaves them out would clear
_opaque_fields = ('is_audit_log_active', 'security_id') + HTTP_SOAP.HealthCheck.FieldList + \
    HTTP_SOAP.Retry.FieldList + HTTP_SOAP.Queue.FieldList + HTTP_SOAP.DLQ.FieldList

# The columns of a generic connection an edit sends back as they are
_own_fields = ('id', 'name', 'type_', 'address', 'pool_size', 'is_active', 'is_internal', 'is_channel', 'is_outconn')

# ################################################################################################################################
# ################################################################################################################################

def _response_to_dict(response:'any_') -> 'anydictnone':
    """ What the endpoint answered, as a dict - the resource it created or the OperationOutcome it turned the save down with.
    """
    if response is None:
        out = None
    elif isinstance(response, dict):
        out = dict(response)
    else:
        out = {'text': str(response)}

    return out

# ################################################################################################################################

def _result_to_dict(result:'any_') -> 'stranydict':
    """ What one save came back with, as a dict.
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

def _send_one(service:'Service', conn_name:'str', data:'anydict') -> 'stranydict':
    """ One save through a connection - with the switch off, an OperationOutcome is the endpoint's answer, not something raised.
    """
    client = service.fhir[conn_name]
    resource = client.resource(_resource_type, **data)

    try:
        result = resource.save()
        out = _result_to_dict(result)
        out['raised'] = ''

    except BaseFHIRError as e:
        out = {
            'is_send_result': False,
            'is_ok': False,
            'response': {'text': str(e)},
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
    """ Saves one resource through an outgoing FHIR connection.
    """

    name = 'test.queue-delivery.send'

    def handle(self) -> 'None':

        raw_request = self.request.raw_request

        conn_name = raw_request['conn_name']
        data = raw_request['data']

        # The headers of a send are HTTP's own - a FHIR connection's headers come from its configuration
        self.response.payload = _send_one(self, conn_name, data)

# ################################################################################################################################
# ################################################################################################################################

class SendMany(Service):
    """ Saves resources through one connection once per document, in this order.
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
    """ Reads one resource through an outgoing FHIR connection - a read that is never a delivery.
    """

    name = 'test.queue-delivery.read'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        client = self.fhir[conn_name]

        try:
            resource = client.get(_resource_type, _read_resource_id)
            out = {
                'is_send_result': False,
                'is_ok': True,
                'response': dict(resource),
            }

        except BaseFHIRError as e:
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
    """ The configuration an outgoing FHIR connection has right now.
    """
    out = service.server.config_manager.outconn_hl7_fhir[conn_name]
    return out

# ################################################################################################################################
# ################################################################################################################################

class GetConnection(Service):
    """ Answers with the configuration an outgoing FHIR connection has right now.
    """

    name = 'test.queue-delivery.get-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        config = _get_config(self, conn_name)

        out:'stranydict' = {
            'conn_type': OutgoingType.FHIR,
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
    """ Changes some fields of an outgoing FHIR connection as the Dashboard does.
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
    """ Creates an outgoing FHIR connection configured like an existing one, under a new name, as the Dashboard does.
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
    """ Deletes an outgoing FHIR connection as the Dashboard does.
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
