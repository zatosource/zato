# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What one invocation of a user-defined service writes to the audit log - a single event under
# the invocation's cid, so it sits in the same flow as the channel that carried the request and
# the connections the service went on to use, with the request, the response and a traceback
# as its bodies.

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
Async_Msg_Key = 'zato.request_ctx.async_msg'

# The attribute holding the channel type the invocation came in through.
Attr_Channel = 'channel'

# ################################################################################################################################
# ################################################################################################################################

def to_body_text(value:'any_') -> 'str':
    """ Returns the text form of a request or a response, whatever a service was given or produced.
    """
    if value is None:
        return ''

    if isinstance(value, str):
        return value

    if isinstance(value, bytes):
        out = value.decode('utf8')
        return out

    # An output payload or a stream serializes itself.
    if hasattr(value, 'getvalue'):
        out = to_body_text(value.getvalue())
        return out

    out = dumps(value)
    return out

# ################################################################################################################################

def resolve_caller(request_ctx:'stranydict', channel_item:'stranydict') -> 'str':
    """ Returns the name of what invoked a service - the invoking service, the channel or the scheduler job.
    """
    if Invoking_Service_Key in request_ctx:
        out = request_ctx[Invoking_Service_Key]
        return out

    if channel_item:
        out = channel_item['name']
        return out

    if Async_Msg_Key in request_ctx:
        async_msg = request_ctx[Async_Msg_Key]
        if 'name' in async_msg:
            out = async_msg['name']
            return out

    return ''

# ################################################################################################################################

def _last_line(text:'str') -> 'str':
    """ Returns the last non-empty line of a traceback, which is the exception itself.
    """
    lines:'strlist' = []

    for line in text.splitlines():
        if line.strip():
            lines.append(line)

    if lines:
        out = lines[-1]
    else:
        out = ''

    return out

# ################################################################################################################################

def record_service_invocation(
    audit_log:'AuditLog',
    service_name:'str',
    cid:'str',
    channel:'str',
    caller:'str',
    request:'any_',
    response:'any_',
    duration_ms:'int',
    error_traceback:'str',
    ) -> 'None':
    """ Records one completed invocation of a service - what it was given and what it returned as bodies,
    the traceback as a third body when it failed.
    """
    request_text = to_body_text(request)
    response_text = to_body_text(response)

    bodies = {
        AuditBody.Request: request_text,
        AuditBody.Response: response_text,
    }

    if error_traceback:
        outcome = AuditOutcome.Error
        status = _last_line(error_traceback)
        bodies[AuditBody.Error] = error_traceback
    else:
        outcome = AuditOutcome.OK
        status = ''

    _ = audit_log.insert(
        AuditSource.Service,
        AuditEvent.Service_Invoked,
        service_name,
        cid=cid,
        endpoint=caller,
        size=len(request_text),
        outcome=outcome,
        status=status,
        duration_ms=duration_ms,
        attrs={Attr_Channel: channel},
        bodies=bodies,
    )

# ################################################################################################################################
# ################################################################################################################################
