# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How one destination of one channel is actually delivered to. There is one adapter per type of
# outgoing connection, each of them reaching the connection through the very facade a service
# would use, so a destination is resolved at the moment of each send and an edit to a connection
# is picked up without anything here being told about it. Every adapter turns the audit log of
# the connection it uses off for the call it makes, the delivery being recorded once, by the
# engine, with the destination it belongs to named on the row. Every adapter reports a rejection
# as part of its result, only a delivery that never got an answer at all raising.

# stdlib
from json import loads
from typing import Protocol

# Zato
from zato.common.api import SMTPMessage
from zato.common.audit_log.common import Ack_Rejected_Marker, AuditClassification, AuditSource
from zato.common.audit_log.request_context import Key_Address, Key_Headers, Key_Method, Key_Params
from zato.common.destination.constants import Default_Method, Default_Params, Default_Path, Default_Subject, \
    Default_To, DestinationOption, DestinationType, Hop_Destination_Name
from zato.common.destination.model import get_option, new_send_result, DestinationException
from zato.common.hl7.mllp.ack import get_ack_rejection
from zato.common.pubsub.outgoing import SendResult
from zato.hl7v2 import parse_hl7
from zato.server.generic.api.outconn_hl7_fhir_audit import get_fhir_rejection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.destination.model import DestinationEntry, HopSendResult
    from zato.common.typing_ import any_, stranydict, strcalldict
    HopSendResult = HopSendResult

# ################################################################################################################################
# ################################################################################################################################

class DestinationConnections(Protocol):
    """ What an adapter needs of whoever it delivers on behalf of - nothing beyond the outgoing
    connections themselves, reached the way a service reaches them. A service satisfies this, and
    so does what a channel with no service of its own delivers through.
    """

    rest:  'any_'
    soap:  'any_'
    mllp:  'any_'
    fhir:  'any_'
    email: 'any_'

# ################################################################################################################################
# ################################################################################################################################

# The method a REST destination is invoked with, by the name the Dashboard offers it under
_rest_invoker_method = {
    'GET':    'get',
    'POST':   'post',
    'PUT':    'put',
    'PATCH':  'patch',
    'DELETE': 'delete',
}

# The methods that carry what is being delivered in their request body
_rest_methods_with_body = ('POST', 'PUT', 'PATCH')

# What every HL7 v2 message opens with - the mark by which the FHIR adapter
# recognizes a message that is to convert to a FHIR bundle on its way out.
_er7_prefix = 'MSH'

# What an SMTP delivery that did not go through is recorded as, the transport saying no more
# than that it failed.
_smtp_rejected_status = 'SMTP message was not sent'

# Which facade a call one outgoing connection recorded on its own behalf is repeated through
_recorded_facade = {
    AuditSource.REST_Outgoing: 'rest',
    AuditSource.SOAP_Outgoing: 'soap',
}

# ################################################################################################################################
# ################################################################################################################################

def http_send_result(response:'any_') -> 'HopSendResult':
    """ Turns what an outgoing REST or SOAP call answered with into a delivery result, shared
    by the live fan-out and by a resend.
    """

    # A connection with the queue switch on answers with what became of the message rather than
    # with a response of its own, so there is no status to read a rejection off.
    if isinstance(response, SendResult):
        out = new_send_result(response)

    # An error status is the endpoint's answer, not a failure to reach it. The status line alone
    # is what the row is classified by, the body travelling as the row's response body.
    elif not response.ok:
        status = f'HTTP {response.status_code} {response.reason}'
        out = new_send_result(response, is_rejected=True, status=status, response_text=response.text)

    else:
        out = new_send_result(response, response_text=response.text)

    return out

# ################################################################################################################################

def is_own_recorded_call(source:'str', details:'stranydict') -> 'bool':
    """ Whether one row is a call an outgoing connection made on its own behalf rather than a
    delivery a channel's fan-out engine made through it. A fan-out row names the destination
    it went to, an own call names none.
    """
    if source in _recorded_facade:
        out = Hop_Destination_Name not in details
    else:
        out = False

    return out

# ################################################################################################################################

def send_recorded(connections:'DestinationConnections', source:'str', connection:'str', details:'stranydict',
    payload:'any_', cid:'str') -> 'HopSendResult':
    """ Repeats one call an outgoing REST or SOAP connection recorded on its own behalf, made to
    the address the call resolved to, with the query string, the caller's headers and the method
    the row carries.
    """
    facade = _recorded_facade[source]
    invoker = getattr(connections, facade)[connection]

    conn = invoker.conn

    # A row written before the address was stored carries none, and a templated connection cannot
    # have one rebuilt without the path parameters the call was made with.
    address = details.get(Key_Address, '')

    if not address:
        if conn.path_params:
            reason = 'has a templated address and this row predates stored request context'
            message = f'Connection `{connection}` {reason}, so the call it recorded cannot be repeated'
            raise DestinationException(message)

        address = conn.address

    method = details.get(Key_Method, Default_Method)
    params = details.get(Key_Params, {})
    headers = details.get(Key_Headers, {})

    response = conn.resend_recorded(cid, method, address, payload, params, headers)

    out = http_send_result(response)
    return out

# ################################################################################################################################

def _send_rest(connections:'DestinationConnections', entry:'DestinationEntry', payload:'any_',
    cid:'str'='') -> 'HopSendResult':
    """ Delivers to an outgoing REST connection, with the method the destination names.
    """
    method = get_option(entry, DestinationOption.Method, Default_Method)

    if method not in _rest_invoker_method:
        raise DestinationException(f'Destination `{entry.name}` cannot be delivered to with method `{method}`')

    invoker = connections.rest[entry.connection]
    function = getattr(invoker, _rest_invoker_method[method])

    # A method with a body carries what is being delivered ..
    if method in _rest_methods_with_body:
        response = function(payload, needs_audit=False)

    # .. and one without it says nothing beyond the call itself.
    else:
        response = function(needs_audit=False)

    out = http_send_result(response)
    return out

# ################################################################################################################################

def _send_mllp(connections:'DestinationConnections', entry:'DestinationEntry', payload:'any_',
    cid:'str'='') -> 'HopSendResult':
    """ Delivers to an outgoing HL7 MLLP connection and returns the text of the acknowledgment it
    answered with - that text, and not the result object around it, is what a channel replying
    from this destination answers its own sender with, whether the acknowledgment accepted
    the message or not.
    """
    invoker = connections.mllp[entry.connection]

    result = invoker.send(payload, needs_audit=False)

    # A connection with the queue switch on answers with what became of the message rather than
    # with an acknowledgment, the way a REST destination with the switch on does
    if isinstance(result, SendResult):
        out = new_send_result(result)
        return out

    ack_text = result.ack_text

    # An AE or an AR is the receiving application saying no, marked as a permanent refusal.
    if rejection := get_ack_rejection(result):
        status = f'{Ack_Rejected_Marker} {rejection}'
        out = new_send_result(ack_text, is_rejected=True, status=status, response_text=ack_text,
            classification=AuditClassification.Permanent)
        return out

    out = new_send_result(ack_text, response_text=ack_text)
    return out

# ################################################################################################################################

def _send_fhir(connections:'DestinationConnections', entry:'DestinationEntry', payload:'any_',
    cid:'str'='') -> 'HopSendResult':
    """ Delivers to an outgoing HL7 FHIR connection, with the method and the path the destination
    names. An HL7 v2 message converts to a FHIR bundle on its way out, which is what lets a channel
    fan out to FHIR destinations with no service of its own.
    """
    method = get_option(entry, DestinationOption.Method, Default_Method)
    path = get_option(entry, DestinationOption.Path, Default_Path)

    if not path:
        raise DestinationException(f'Destination `{entry.name}` has no path to deliver to')

    # A channel with no service hands over the message as it arrived over the wire,
    # which may still be bytes.
    if isinstance(payload, bytes):
        payload = payload.decode('utf-8')

    if isinstance(payload, str):

        # A read carries no body at all, so there is nothing to parse.
        if not payload:
            payload = None

        # An HL7 v2 message converts to the FHIR bundle the destination receives ..
        elif payload.startswith(_er7_prefix):
            message = parse_hl7(payload)
            payload = message.to_fhir_dict()

        # .. and any other text is already a FHIR resource in its JSON form.
        else:
            payload = loads(payload)

    client = connections.fhir[entry.connection]
    params = get_option(entry, DestinationOption.Params, Default_Params)

    # The client raises for every status fhirpy raises for, with the response the status came
    # on riding along on the exception.
    try:
        response = client._do_request(method, path, data=payload, params=params, needs_audit=False)

    except Exception as e:
        rejected_response = getattr(e, 'zato_response', None)

        # Nothing came back at all, so this is a failure to deliver rather than an answer.
        if rejected_response is None:
            raise

        status = f'HTTP {rejected_response.status_code} {rejected_response.reason}'
        _, body = get_fhir_rejection(rejected_response)

        out = new_send_result(body, is_rejected=True, status=status, response_text=rejected_response.text)

    else:
        out = new_send_result(response)

    return out

# ################################################################################################################################

def _send_smtp(connections:'DestinationConnections', entry:'DestinationEntry', payload:'any_',
    cid:'str'='') -> 'HopSendResult':
    """ Delivers to an outgoing SMTP connection, as the body of a message to the recipient
    and under the subject line the destination names.
    """
    if connections.email is None:
        raise DestinationException(f'Destination `{entry.name}` cannot be delivered to, e-mail is not enabled')

    to = get_option(entry, DestinationOption.To, Default_To)

    if not to:
        raise DestinationException(f'Destination `{entry.name}` has no recipient to deliver to')

    message = SMTPMessage()

    message.to = to
    message.subject = get_option(entry, DestinationOption.Subject, Default_Subject)
    message.body = payload

    item = connections.email.smtp[entry.connection]

    # The connection's own message-sent row and the hop row that the delivery engine writes
    # describe one delivery, so they share the correlation id.
    is_sent = item.conn.send(message, cid=cid)

    # The transport reports a message it could not send by answering no rather than by raising.
    if not is_sent:
        out = new_send_result(is_sent, is_rejected=True, status=_smtp_rejected_status)
        return out

    out = new_send_result(is_sent)
    return out

# ################################################################################################################################
# ################################################################################################################################

# Which adapter delivers to which type of destination - the keys are the type ids the Dashboard writes
_adapters:'strcalldict' = {
    DestinationType.REST: _send_rest,
    DestinationType.MLLP: _send_mllp,
    DestinationType.FHIR: _send_fhir,
    DestinationType.SMTP: _send_smtp,
}

# ################################################################################################################################

def send(connections:'DestinationConnections', entry:'DestinationEntry', payload:'any_', cid:'str'='') -> 'any_':
    """ Delivers one payload to one destination, whatever the type of connection behind it.
    """
    if adapter := _adapters.get(entry.type):
        out = adapter(connections, entry, payload, cid)

    # .. a type nothing delivers to should never have been stored in the first place.
    else:
        raise DestinationException(f'Destination `{entry.name}` is of a type nothing delivers to, `{entry.type}`')

    return out

# ################################################################################################################################
# ################################################################################################################################
