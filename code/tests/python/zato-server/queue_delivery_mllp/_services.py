# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services of the outgoing MLLP suite - what is MLLP's own of the contract every type's suite fulfils. The
# helpers that turn a document into an HL7 message and back live here too, because this file is copied to the
# server's pickup directory on its own, and the suite's type module imports them from here.

# stdlib
import re
from datetime import datetime, timezone
from json import dumps, loads

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.hl7.mllp.ack import AckResult, new_control_id
from zato.common.pubsub.outgoing import OutgoingType, SendResult
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The opaque attributes, which an edit that leaves them out would clear
_opaque_fields = ('is_audit_log_active', 'should_log_messages', 'logging_level', 'max_msg_size', 'read_buffer_size',
    'recv_timeout', 'start_seq', 'end_seq', 'max_wait_time', 'circuit_breaker_threshold_percent',
    'circuit_breaker_window_seconds', 'circuit_breaker_reset_seconds', 'tls_cert_path', 'tls_key_path', 'tls_ca_path') + \
    HTTP_SOAP.Retry.FieldList + HTTP_SOAP.Queue.FieldList + HTTP_SOAP.DLQ.FieldList

# The columns of a generic connection an edit sends back as they are
_own_fields = ('id', 'name', 'type_', 'address', 'pool_size', 'is_active', 'is_internal', 'is_channel', 'is_outconn')

# ################################################################################################################################
# ################################################################################################################################

# What every message of the suite is - an admission, from the suite's own application to the receiver's
Message_Type = 'ADT^A01'
Sending_Application = 'ZATO'
Sending_Facility = 'TEST'
Receiving_Application = 'RECEIVER'
Receiving_Facility = 'TEST'
Processing_Id = 'P'
Version_Id = '2.5'

# The segment a document travels in, as JSON in its first field
Document_Segment = 'ZQD'

Segment_Separator = '\r'
Field_Separator = '|'
Encoding_Characters = '^~\\&'

# How MSH-7 is written
_timestamp_format = '%Y%m%d%H%M%S'

# The characters a field cannot carry as they are, and the escape sequence each becomes
_escapes = (
    ('\\', '\\E\\'),
    ('|', '\\F\\'),
    ('^', '\\S\\'),
    ('~', '\\R\\'),
    ('&', '\\T\\'),
)

_unescapes = {escaped: plain for plain, escaped in _escapes}
_unescape_pattern = re.compile(r'\\[EFSRT]\\')

# ################################################################################################################################
# ################################################################################################################################

def escape_field(value:'str') -> 'str':
    """ A field's text with the delimiters escaped the way HL7 escapes them.
    """
    out = value

    for plain, escaped in _escapes:
        out = out.replace(plain, escaped)

    return out

# ################################################################################################################################

def unescape_field(value:'str') -> 'str':
    """ A field's text with the escape sequences turned back into the characters they stand for.
    """
    out = _unescape_pattern.sub(lambda match: _unescapes[match.group(0)], value)
    return out

# ################################################################################################################################

def build_message(document:'anydict', control_id:'str'='') -> 'str':
    """ A document as the ER7 message the suite sends it as - an MSH segment and the document's segment after it.
    """
    if not control_id:
        control_id = new_control_id()

    timestamp = datetime.now(timezone.utc).strftime(_timestamp_format)

    msh = Field_Separator.join([
        'MSH',
        Encoding_Characters,
        Sending_Application,
        Sending_Facility,
        Receiving_Application,
        Receiving_Facility,
        timestamp,
        '',
        Message_Type,
        control_id,
        Processing_Id,
        Version_Id,
    ])

    document_segment = Field_Separator.join([Document_Segment, escape_field(dumps(document))])

    out = Segment_Separator.join([msh, document_segment]) + Segment_Separator
    return out

# ################################################################################################################################

def document_of_message(message_text:'str') -> 'anydict':
    """ The document an ER7 message of the suite carries in its document segment.
    """
    for segment in message_text.split(Segment_Separator):

        if segment.startswith(Document_Segment + Field_Separator):
            _, field = segment.split(Field_Separator, 1)
            out = loads(unescape_field(field))
            return out

    raise ValueError(f'No {Document_Segment} segment in `{message_text!r}`')

# ################################################################################################################################

def control_id_of_message(message_text:'str') -> 'str':
    """ MSH-10 of an ER7 message.
    """
    msh = message_text.split(Segment_Separator, 1)[0]
    out = msh.split(Field_Separator)[9]

    return out

# ################################################################################################################################
# ################################################################################################################################

def _ack_to_dict(ack:'any_') -> 'anydictnone':
    """ What the receiving system answered, as a dict - the acknowledgment as the connection read it.
    """
    if ack is None:
        out = None

    elif isinstance(ack, AckResult):
        out = {
            'ack_code': ack.ack_code,
            'is_accepted': ack.is_accepted,
            'should_retry': ack.should_retry,
            'error_text': ack.error_text,
            'ack_text': ack.ack_text,
        }

    else:
        out = {'text': str(ack)}

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
            'response': _ack_to_dict(result.response),
        }
    else:
        out = {
            'is_send_result': False,
            'is_ok': result.is_accepted,
            'response': _ack_to_dict(result),
        }

    return out

# ################################################################################################################################

def _send_one(service:'Service', conn_name:'str', data:'anydict') -> 'stranydict':
    """ One send through a connection - with the switch off, a negative acknowledgment is the receiving system's answer,
    not something raised, and a send no acknowledgment came back from raises.
    """
    message_text = build_message(data)

    try:
        result = service.mllp[conn_name].send(message_text)
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
    """ Sends one message through an outgoing MLLP connection.
    """

    name = 'test.queue-delivery.send'

    def handle(self) -> 'None':

        raw_request = self.request.raw_request

        conn_name = raw_request['conn_name']
        data = raw_request['data']

        # An MLLP message has no headers - what a scenario hands over as headers has nowhere to go
        self.response.payload = _send_one(self, conn_name, data)

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
    """ Pings an outgoing MLLP connection - a connection opened and closed again, which is never a delivery.
    """

    name = 'test.queue-delivery.read'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        # Our response to produce
        out:'anydict'

        try:
            self.mllp[conn_name].ping()
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
    """ The configuration an outgoing MLLP connection has right now.
    """
    out = service.server.config_manager.outconn_hl7_mllp[conn_name]
    return out

# ################################################################################################################################
# ################################################################################################################################

class GetConnection(Service):
    """ Answers with the configuration an outgoing MLLP connection has right now.
    """

    name = 'test.queue-delivery.get-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        config = _get_config(self, conn_name)

        out:'stranydict' = {
            'conn_type': OutgoingType.MLLP,
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
    """ Changes some fields of an outgoing MLLP connection as the Dashboard does.
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
    """ Creates an outgoing MLLP connection configured like an existing one, under a new name, as the Dashboard does.
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
    """ Deletes an outgoing MLLP connection as the Dashboard does.
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
