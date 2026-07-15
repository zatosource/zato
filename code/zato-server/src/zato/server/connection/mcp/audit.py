# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydictnone, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# Markers used as the method of events that have no JSON-RPC method of their own -
# a batch carries many methods in one HTTP request and a session delete is a plain HTTP DELETE.
Method_Batch          = 'batch'
Method_Session_Delete = 'session-delete'

# What a request whose method could not be parsed at all audits as
Method_Unknown = 'unknown'

# The fixed mapping of methods to audit event types - methods outside this set,
# e.g. ping or notifications/initialized, audit as their literal method name.
_method_to_event = {
    'initialize':           AuditEvent.MCP_Initialize,
    'tools/list':           AuditEvent.MCP_Tools_List,
    'tools/call':           AuditEvent.MCP_Tools_Call,
    Method_Batch:           AuditEvent.MCP_Batch,
    Method_Session_Delete:  AuditEvent.MCP_Session_Delete,
}

# HTTP status codes in this range mean success
_http_success_min = 200
_http_success_max = 299

# How many decimal places the duration is stored with
_duration_precision = 2

# ################################################################################################################################
# ################################################################################################################################

def _find_error(body:'any_') -> 'anydictnone':
    """ Returns the JSON-RPC error object of a response body - for a batch response,
    the error of its first erroring element - or None when there is no error at all.
    """

    # A single response carries the error at its top level ..
    if isinstance(body, dict):
        out = body.get('error')
        return out

    # .. a batch is an array of single responses.
    if isinstance(body, list):
        for element in body:
            if isinstance(element, dict):
                if error := element.get('error'):
                    out = error
                    return out

    return None

# ################################################################################################################################

def build_audit_event(
    gateway_name:'str',
    sec_def_name:'str',
    cid:'str',
    method:'strnone',
    tool_name:'strnone',
    session_id:'strnone',
    remote_address:'str',
    response_body:'any_',
    response_size:'int',
    status_code:'int',
    duration_ms:'float',
    request_size:'int',
    ) -> 'stranydict':
    """ Builds the keyword dict for one AuditLog.insert call out of plain inputs -
    this is the published column mapping of the MCP audit log. The request and response
    payloads are never included, only their sizes are.
    """

    # A request that could not be parsed has no method to audit under ..
    if method is None:
        method = Method_Unknown

    # .. known methods map to their event types, anything else audits as its literal name ..
    if method in _method_to_event:
        event_type = _method_to_event[method]
    else:
        event_type = method

    # .. only tools/call events carry a tool name ..
    if tool_name is None:
        tool_name = ''

    # .. and only requests that carried or created a session have one to record ..
    if session_id is None:
        session_id = ''

    # .. the outcome is an error when the HTTP status is not 2xx
    # or when the JSON-RPC response body carries an error object ..
    error = _find_error(response_body)
    is_http_success = _http_success_min <= status_code <= _http_success_max

    if is_http_success and error is None:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    # .. the fields without a column of their own go into the data document ..
    data:'stranydict' = {
        'remote_address': remote_address,
        'method': method,
        'duration_ms': round(duration_ms, _duration_precision),
        'request_size': request_size,
    }

    # .. errors additionally record what the response reported ..
    if error is not None:
        data['error_code'] = error.get('code')
        data['error_message'] = error.get('message')

    # .. and this is the whole published mapping.
    out:'stranydict' = {
        'source': AuditSource.MCP,
        'event_type': event_type,
        'object_name': gateway_name,
        'cid': cid,
        'endpoint': tool_name,
        'ext_client_id': sec_def_name,
        'sub_key': session_id,
        'size': response_size,
        'outcome': outcome,
        'data': dumps(data),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
