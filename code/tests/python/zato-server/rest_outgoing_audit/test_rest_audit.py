# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing REST call leaves a request-sent and a response-received row under one
# correlation id, the response row carrying the HTTP status it came with. A health check's
# ping leaves the same pair, under the connection's health source rather than its traffic one,
# which is what lets a check's failures be counted apart from a call's.

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.json_internal import loads

# Test support
from rest_stub import new_rest_wrapper, new_soap_wrapper, rest_audit_env, Address_Host, Address_Path, Connection_Name, \
    ResponseStub

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

        # The stored document is the resubmit convention - the payload plus the method
        # a per-hop resend needs to repeat the exact same call - while the size recorded
        # is the wire size of the payload itself.
        assert loads(request_sent['data']) == {'payload': 'The request body', 'method': 'POST'}
        assert request_sent['size'] == len('The request body')

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

        # A ping goes out with no body, and its stored document says so - the empty payload
        # plus the method, which is what makes even a ping row repeatable per hop.
        assert loads(request_sent['data']) == {'payload': '', 'method': 'HEAD'}
        assert request_sent['size'] == 0

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

def test_a_ping_writes_the_health_source(tmp_path:'os.PathLike') -> 'None':
    """ Both rows a ping leaves belong to the connection's health source, and both still
    name the connection, so a check is found where the connection is looked for.
    """
    with rest_audit_env(tmp_path):

        wrapper = new_rest_wrapper()
        wrapper.invoke_http = _replying_invoke_http(ResponseStub(OK, 'OK', ''))

        _ = wrapper.ping(_cid)

        events = _get_events()
        assert len(events) == 2

        for event in events:
            assert event['source'] == AuditSource.REST_Outgoing_Health
            assert event['object_name'] == Connection_Name

# ################################################################################################################################

def test_a_failed_ping_writes_the_health_source(tmp_path:'os.PathLike') -> 'None':
    """ A ping that never got an answer is recorded on the health source too - the error
    rows are the ones a failure streak is counted from.
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

        for event in events:
            assert event['source'] == AuditSource.REST_Outgoing_Health

        response_received = events[1]
        assert response_received['outcome'] == AuditOutcome.Error

# ################################################################################################################################

def test_business_traffic_keeps_the_traffic_source(tmp_path:'os.PathLike') -> 'None':
    """ A regular call is unaffected by what a ping does - both its rows stay on the
    connection's traffic source.
    """
    with rest_audit_env(tmp_path):

        wrapper = new_rest_wrapper()
        wrapper.invoke_http = _replying_invoke_http(ResponseStub(OK, 'OK', '{"result":"created"}'))

        _ = wrapper.post(_cid, 'The request body')

        events = _get_events()
        assert len(events) == 2

        for event in events:
            assert event['source'] == AuditSource.REST_Outgoing

# ################################################################################################################################

def test_a_ping_and_a_call_land_on_different_sources(tmp_path:'os.PathLike') -> 'None':
    """ One connection pinged and called writes to two sources under the one name,
    which is the whole point - the same object measured as two streams.
    """
    with rest_audit_env(tmp_path):

        wrapper = new_rest_wrapper()
        wrapper.invoke_http = _replying_invoke_http(ResponseStub(OK, 'OK', ''))

        _ = wrapper.ping(_cid)
        _ = wrapper.post(_cid, 'The request body')

        events = _get_events()
        assert len(events) == 4

        sources = set()
        object_names = set()

        for event in events:
            sources.add(event['source'])
            object_names.add(event['object_name'])

        assert sources == {AuditSource.REST_Outgoing_Health, AuditSource.REST_Outgoing}
        assert object_names == {Connection_Name}

# ################################################################################################################################

def test_a_soap_ping_writes_the_soap_health_source(tmp_path:'os.PathLike') -> 'None':
    """ The transport decides which health source a check writes to, the same way it decides
    which traffic source a call writes to.
    """
    with rest_audit_env(tmp_path):

        wrapper = new_soap_wrapper()
        wrapper.invoke_http = _replying_invoke_http(ResponseStub(OK, 'OK', ''))

        _ = wrapper.ping(_cid)

        events = _get_events()
        assert len(events) == 2

        for event in events:
            assert event['source'] == AuditSource.SOAP_Outgoing_Health
            assert event['object_name'] == Connection_Name

# ################################################################################################################################
# ################################################################################################################################
