# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing REST call leaves a request-sent and a response-received row under one
# correlation id, the response row carrying the HTTP status it came with - and a ping
# is traffic like any other, so it leaves the same pair.

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource

# Test support
from rest_stub import new_rest_wrapper, rest_audit_env, Address_Host, Address_Path, Connection_Name, ResponseStub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from zato.common.typing_ import any_, anylist

    os = os

# ################################################################################################################################
# ################################################################################################################################

# The cid a caller hands the invocation
_cid = 'cid-rest-audit-1'

# What the connection points at, as the events record it
_address = Address_Host + Address_Path

# What a refusing endpoint answers with
_error_body = 'The endpoint could not process the request'

# What a dead endpoint fails with
_connection_error = 'The endpoint went away'

# ################################################################################################################################
# ################################################################################################################################

def _get_events() -> 'anylist':
    """ Everything the audit log holds, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################

def _replying_invoke_http(response:'ResponseStub') -> 'any_':
    """ Builds an invoke_http stand-in that answers every call with the given response.
    """
    def invoke_http(cid:'any_', method:'any_', address:'any_', data:'any_', headers:'any_', hooks:'any_',
        *args:'any_', **kwargs:'any_') -> 'ResponseStub':
        return response

    return invoke_http

# ################################################################################################################################

def _raising_invoke_http() -> 'any_':
    """ Builds an invoke_http stand-in that fails the way a dead endpoint makes it fail.
    """
    def invoke_http(cid:'any_', method:'any_', address:'any_', data:'any_', headers:'any_', hooks:'any_',
        *args:'any_', **kwargs:'any_') -> 'ResponseStub':
        raise Exception(_connection_error)

    return invoke_http

# ################################################################################################################################
# ################################################################################################################################

def test_a_response_carries_its_http_status(tmp_path:'os.PathLike') -> 'None':
    """ A call that went through leaves a pair under one cid, and the response row
    carries the HTTP status the endpoint answered with.
    """
    with rest_audit_env(tmp_path):

        wrapper = new_rest_wrapper()
        wrapper.invoke_http = _replying_invoke_http(ResponseStub(OK, 'OK', '{"result":"created"}'))

        _ = wrapper.post(_cid, 'The request body')

        events = _get_events()
        assert len(events) == 2

        request_sent = events[0]

        assert request_sent['source'] == AuditSource.REST_Outgoing
        assert request_sent['event_type'] == AuditEvent.Request_Sent
        assert request_sent['object_name'] == Connection_Name
        assert request_sent['outcome'] == AuditOutcome.OK
        assert request_sent['cid'] == _cid
        assert request_sent['endpoint'] == f'POST {_address}'

        # The request went out before any response existed, so it carries no status
        assert request_sent['status'] == ''

        response_received = events[1]

        assert response_received['event_type'] == AuditEvent.Response_Received
        assert response_received['outcome'] == AuditOutcome.OK
        assert response_received['cid'] == _cid
        assert response_received['status'] == f'{OK} OK'

# ################################################################################################################################

def test_an_error_response_keeps_its_status(tmp_path:'os.PathLike') -> 'None':
    """ A refused call's response row says which status refused it, not merely that
    something went wrong.
    """
    with rest_audit_env(tmp_path):

        wrapper = new_rest_wrapper()
        wrapper.invoke_http = _replying_invoke_http(
            ResponseStub(INTERNAL_SERVER_ERROR, 'Internal Server Error', _error_body))

        _ = wrapper.post(_cid, 'The request body')

        events = _get_events()
        assert len(events) == 2

        response_received = events[1]

        assert response_received['event_type'] == AuditEvent.Response_Received
        assert response_received['outcome'] == AuditOutcome.Error
        assert response_received['status'] == f'{INTERNAL_SERVER_ERROR} Internal Server Error'
        assert response_received['data'] == _error_body

# ################################################################################################################################

def test_a_ping_writes_a_request_response_pair(tmp_path:'os.PathLike') -> 'None':
    """ A ping leaves the same pair a regular invocation does, under one cid,
    with the response row carrying the HTTP status.
    """
    with rest_audit_env(tmp_path):

        wrapper = new_rest_wrapper()
        wrapper.invoke_http = _replying_invoke_http(ResponseStub(OK, 'OK', ''))

        _ = wrapper.ping(_cid)

        events = _get_events()
        assert len(events) == 2

        request_sent = events[0]

        assert request_sent['event_type'] == AuditEvent.Request_Sent
        assert request_sent['outcome'] == AuditOutcome.OK
        assert request_sent['cid'] == _cid
        assert request_sent['endpoint'] == f'HEAD {_address}'

        response_received = events[1]

        assert response_received['event_type'] == AuditEvent.Response_Received
        assert response_received['outcome'] == AuditOutcome.OK
        assert response_received['cid'] == _cid
        assert response_received['status'] == f'{OK} OK'

# ################################################################################################################################

def test_a_failed_ping_writes_the_error(tmp_path:'os.PathLike') -> 'None':
    """ A ping the endpoint never answered is recorded with what stopped it,
    before the caller learns about the failure.
    """
    with rest_audit_env(tmp_path):

        wrapper = new_rest_wrapper()
        wrapper.invoke_http = _raising_invoke_http()

        try:
            _ = wrapper.ping(_cid)
        except Exception as e:
            assert _connection_error in str(e)
        else:
            raise AssertionError('The ping should have raised')

        events = _get_events()
        assert len(events) == 2

        response_received = events[1]

        assert response_received['event_type'] == AuditEvent.Response_Received
        assert response_received['outcome'] == AuditOutcome.Error
        assert response_received['data'] == _connection_error

        # No response ever arrived, so there is no status to record
        assert response_received['status'] == ''

# ################################################################################################################################

def test_a_ping_of_an_unaudited_connection_writes_nothing(tmp_path:'os.PathLike') -> 'None':
    """ A connection whose audit log is off pings and leaves no trace.
    """
    with rest_audit_env(tmp_path):

        wrapper = new_rest_wrapper(is_audit_log_active=False)
        wrapper.invoke_http = _replying_invoke_http(ResponseStub(OK, 'OK', ''))

        _ = wrapper.ping(_cid)

        assert _get_events() == []

# ################################################################################################################################
# ################################################################################################################################
