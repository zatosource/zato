# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# Zato
from zato.common.audit_log.common import AuditBody, AuditEvent, AuditOutcome, AuditSource
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import any_, stranydict, strlist
    AuditLog = AuditLog
    any_ = any_
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The request context key under which a service invoking another one leaves its own name.
Invoking_Service_Key = 'zato.request_ctx.invoking_service'

# The request context key under which the config manager leaves the message that triggered the invocation.
_async_message_key = 'zato.request_ctx.async_msg'

# The attribute holding the channel type the invocation came in through.
Attribute_Channel = 'channel'

# What is recorded when there is no caller, no body or no error line to record.
_empty = ''

# ################################################################################################################################
# ################################################################################################################################

def to_body_text(value:'any_') -> 'str':
    """ Returns the text form of a request or a response.
    """
    if value is None:
        out = _empty

    elif isinstance(value, str):
        out = value

    elif isinstance(value, bytes):
        out = value.decode('utf8')

    # An output payload or a stream serializes itself.
    elif hasattr(value, 'getvalue'):
        payload = value.getvalue()
        out = to_body_text(payload)

    else:
        out = dumps(value)

    return out

# ################################################################################################################################

def resolve_caller(request_ctx:'stranydict', channel_item:'stranydict') -> 'str':
    """ Returns the name of what invoked a service - the invoking service, the channel or the triggering message.
    """
    if invoking_service := request_ctx.get(Invoking_Service_Key):
        out = invoking_service

    elif channel_item:
        out = channel_item['name']

    elif async_message := request_ctx.get(_async_message_key):
        if message_name := async_message.get('name'):
            out = message_name
        else:
            out = _empty

    else:
        out = _empty

    return out

# ################################################################################################################################

def _last_line(text:'str') -> 'str':
    """ Returns the last non-empty line of a traceback.
    """
    lines:'strlist' = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            lines.append(line)

    if lines:
        out = lines[-1]
    else:
        out = _empty

    return out

# ################################################################################################################################

def record_service_request(
    audit_log:'AuditLog',
    service_name:'str',
    cid:'str',
    channel:'str',
    caller:'str',
    request:'any_',
    ) -> 'None':
    """ Records the request a service was given, before the service runs.
    """
    request_text = to_body_text(request)
    request_size = len(request_text)

    attrs  = {Attribute_Channel: channel}
    bodies = {AuditBody.Request: request_text}

    _ = audit_log.insert(
        AuditSource.Service,
        AuditEvent.Service_Request,
        service_name,
        cid=cid,
        endpoint=caller,
        size=request_size,
        attrs=attrs,
        bodies=bodies,
    )

# ################################################################################################################################

def record_service_response(
    audit_log:'AuditLog',
    service_name:'str',
    cid:'str',
    channel:'str',
    caller:'str',
    response:'any_',
    duration_milliseconds:'int',
    error_traceback:'str',
    ) -> 'None':
    """ Records the response a service returned, with the traceback as a second body if it failed.
    """
    response_text = to_body_text(response)
    response_size = len(response_text)

    attrs  = {Attribute_Channel: channel}
    bodies = {AuditBody.Response: response_text}

    if error_traceback:
        outcome = AuditOutcome.Error
        status = _last_line(error_traceback)
        bodies[AuditBody.Error] = error_traceback
    else:
        outcome = AuditOutcome.OK
        status = _empty

    _ = audit_log.insert(
        AuditSource.Service,
        AuditEvent.Service_Response,
        service_name,
        cid=cid,
        endpoint=caller,
        size=response_size,
        outcome=outcome,
        status=status,
        duration_ms=duration_milliseconds,
        attrs=attrs,
        bodies=bodies,
    )

# ################################################################################################################################
# ################################################################################################################################
