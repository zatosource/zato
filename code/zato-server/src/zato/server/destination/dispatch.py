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
# engine, with the destination it belongs to named on the row.

# stdlib
from json import loads
from typing import Protocol

# Zato
from zato.common.api import SMTPMessage
from zato.common.destination.constants import Default_Method, Default_Path, Default_Subject, Default_To, \
    DestinationOption, DestinationType
from zato.common.destination.model import get_option, DestinationException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.destination.model import DestinationEntry
    from zato.common.typing_ import any_, strcalldict

# ################################################################################################################################
# ################################################################################################################################

class DestinationConnections(Protocol):
    """ What an adapter needs of whoever it delivers on behalf of - nothing beyond the outgoing
    connections themselves, reached the way a service reaches them. A service satisfies this, and
    so does what a channel with no service of its own delivers through.
    """

    rest:  'any_'
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

# ################################################################################################################################
# ################################################################################################################################

def _send_rest(connections:'DestinationConnections', entry:'DestinationEntry', payload:'any_', cid:'str'='') -> 'any_':
    """ Delivers to an outgoing REST connection, with the method the destination names.
    """
    method = get_option(entry, DestinationOption.Method, Default_Method)

    if method not in _rest_invoker_method:
        raise DestinationException(f'Destination `{entry.name}` cannot be delivered to with method `{method}`')

    invoker = connections.rest[entry.connection]
    function = getattr(invoker, _rest_invoker_method[method])

    # A method with a body carries what is being delivered ..
    if method in _rest_methods_with_body:
        out = function(payload, needs_audit=False)

    # .. and one without it says nothing beyond the call itself.
    else:
        out = function(needs_audit=False)

    return out

# ################################################################################################################################

def _send_mllp(connections:'DestinationConnections', entry:'DestinationEntry', payload:'any_', cid:'str'='') -> 'any_':
    """ Delivers to an outgoing HL7 MLLP connection and returns the text of the acknowledgment it
    answered with - that text, and not the result object around it, is what a channel replying
    from this destination answers its own sender with.
    """
    invoker = connections.mllp[entry.connection]

    result = invoker.send(payload, needs_audit=False)

    out = result.ack_text
    return out

# ################################################################################################################################

def _send_fhir(connections:'DestinationConnections', entry:'DestinationEntry', payload:'any_', cid:'str'='') -> 'any_':
    """ Delivers to an outgoing HL7 FHIR connection, with the method and the path the destination names.
    """
    method = get_option(entry, DestinationOption.Method, Default_Method)
    path = get_option(entry, DestinationOption.Path, Default_Path)

    if not path:
        raise DestinationException(f'Destination `{entry.name}` has no path to deliver to')

    # A FHIR resource goes out as a document, so what arrives here as text is that document in its JSON form
    if isinstance(payload, str):
        payload = loads(payload)

    client = connections.fhir[entry.connection]

    out = client._do_request(method, path, data=payload, needs_audit=False)
    return out

# ################################################################################################################################

def _send_smtp(connections:'DestinationConnections', entry:'DestinationEntry', payload:'any_', cid:'str'='') -> 'any_':
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
    out = item.conn.send(message, cid=cid)
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
