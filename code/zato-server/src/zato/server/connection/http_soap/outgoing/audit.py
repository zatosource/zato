# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import URL_TYPE
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.common import classify_transport_error
from zato.common.json_ import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.server.connection.http_soap.outgoing import BaseHTTPSOAPWrapper
    from zato.server.connection.http_soap.outgoing.common import Response

# ################################################################################################################################
# ################################################################################################################################

def get_audit_source(transport:'str', is_health_check:'bool') -> 'str':
    """ The audit source an outgoing connection's events go under - by its transport, and a health check's own
    pings go to the connection's health source instead of its traffic one, which is what lets a check's failures
    be counted on their own.
    """
    if transport == URL_TYPE.PLAIN_HTTP:
        if is_health_check:
            out = AuditSource.REST_Outgoing_Health
        else:
            out = AuditSource.REST_Outgoing
    else:
        if is_health_check:
            out = AuditSource.SOAP_Outgoing_Health
        else:
            out = AuditSource.SOAP_Outgoing

    return out

# ################################################################################################################################

def insert_audit_event(
    wrapper:'BaseHTTPSOAPWrapper',
    cid:'str',
    event_type:'str',
    endpoint:'str',
    outcome:'str',
    data:'any_',
    status:'str' = '',
    method:'str' = '',
    *,
    is_health_check:'bool' = False,
) -> 'None':
    """ Writes one audit event describing a request sent to or a response received
    from an outgoing REST or SOAP connection. A request-sent event names the method
    it went out with and is stored as the resubmit convention document,
    which is what makes it repeatable per hop later.
    """

    # Payloads reach here in whatever shape their caller had them in - bytes as they went on the
    # wire, which are decoded with what cannot be decoded replaced ..
    if isinstance(data, bytes):
        data = data.decode('utf-8', errors='replace')

    # .. or an object such as a dict or a multipart encoder, which is described rather than decoded.
    elif not isinstance(data, str):
        data = str(data)

    # .. the size recorded is always the wire size of the payload itself ..
    size = len(data)

    # .. a request-sent event stores the resubmit convention document - the payload plus
    # .. the method a per-hop resend needs to repeat the exact same call ..
    if method:
        data = dumps({'payload': data, 'method': method})

    # .. the source depends on the connection's transport, and on whether this is
    # .. the connection's own health check rather than the traffic it carries ..
    source = get_audit_source(wrapper.config['transport'], is_health_check)

    # .. now, write out the event.
    wrapper.audit_log.insert(
        source,
        event_type,
        wrapper.config['name'],
        cid=cid,
        endpoint=endpoint,
        size=size,
        outcome=outcome,
        status=status,
        data=data,
    )

# ################################################################################################################################

def record_request_sent(
    wrapper:'BaseHTTPSOAPWrapper',
    cid:'str',
    endpoint:'str',
    data:'any_',
    method:'str',
    *,
    is_health_check:'bool' = False,
) -> 'None':
    """ The first event of a call's pair - the request as it went out, with the method a resend repeats it with.
    """
    insert_audit_event(wrapper, cid, AuditEvent.Request_Sent, endpoint, AuditOutcome.OK, data,
        method=method, is_health_check=is_health_check)

# ################################################################################################################################

def record_transport_error(
    wrapper:'BaseHTTPSOAPWrapper',
    cid:'str',
    endpoint:'str',
    exception:'Exception',
    *,
    is_health_check:'bool' = False,
) -> 'None':
    """ The second event of a call's pair when no response arrived - sharing the request's CID and naming
    how the call failed in the status, the way a response names its HTTP status.
    """
    insert_audit_event(wrapper, cid, AuditEvent.Response_Received, endpoint, AuditOutcome.Error, str(exception),
        status=classify_transport_error(exception), is_health_check=is_health_check)

# ################################################################################################################################

def record_response_received(
    wrapper:'BaseHTTPSOAPWrapper',
    cid:'str',
    endpoint:'str',
    response:'Response',
    *,
    is_health_check:'bool' = False,
) -> 'None':
    """ The second event of a call's pair - the response, sharing the request's CID, with the HTTP status
    it came with in whole, so a 500 reads as itself and not merely as an error outcome.
    """
    if response.ok:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    status = f'{response.status_code} {response.reason}'

    insert_audit_event(wrapper, cid, AuditEvent.Response_Received, endpoint, outcome, response.text,
        status=status, is_health_check=is_health_check)

# ################################################################################################################################
# ################################################################################################################################
