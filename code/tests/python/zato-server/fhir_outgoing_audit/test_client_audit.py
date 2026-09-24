# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing FHIR call leaves a request-sent and a response-received row under one correlation id, the response
# row carrying the HTTP status it came with in whole and, when the body is an OperationOutcome, the code of its
# first issue as the application outcome. A call that never got a response names how it failed instead. A health
# check's ping leaves the same pair under the connection's health source, whether or not the audit log is on.

# stdlib
from http.client import INTERNAL_SERVER_ERROR, NOT_FOUND, OK, UNAUTHORIZED

# fhirpy
from fhirpy.base.exceptions import AuthorizationError, OperationOutcome, ResourceNotFound

# pytest
import pytest

# requests
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.common import TransportStatus
from zato.common.json_internal import loads
from zato.common.typing_ import cast_

# Test support
from fhir_stub import fhir_audit_env, new_fhir_client, operation_outcome, unreached_address, Connection_Name, FHIRStandIn

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from zato.common.typing_ import anylist, strdict

    os = os

# ################################################################################################################################
# ################################################################################################################################

# The cid a caller hands the invocation
_cid = 'cid-fhir-audit-1'

# The resource a call reads
_patient_path = 'Patient/1'

# What a good read answers with
_patient_body = '{"resourceType":"Patient","id":"1"}'

# The path a health check reads
_ping_path = '/CapabilityStatement'

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

def _get_attrs(event_id:'int') -> 'strdict':
    """ The searchable attributes of one event, by name.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.name, event_attr_table.c.value)
    query = query.where(event_attr_table.c.event_id == event_id)

    with engine.connect() as connection:
        out = {row.name: row.value for row in connection.execute(query)}

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_good_response_carries_its_status_and_no_outcome(tmp_path:'os.PathLike') -> 'None':
    """ A read that went through leaves a pair under one cid, the response row carrying `200 OK`
    and no application outcome, since nothing went wrong to name.
    """
    with fhir_audit_env(tmp_path), FHIRStandIn(OK, _patient_body) as stand_in:

        client = new_fhir_client(stand_in.address)
        result = cast_('strdict', client._do_request('get', _patient_path, cid=_cid))

        assert result['resourceType'] == 'Patient'

        events = _get_events()
        assert len(events) == 2

        request_sent = events[0]

        assert request_sent['source'] == AuditSource.FHIR
        assert request_sent['event_type'] == AuditEvent.Request_Sent
        assert request_sent['object_name'] == Connection_Name
        assert request_sent['outcome'] == AuditOutcome.OK
        assert request_sent['cid'] == _cid
        assert request_sent['endpoint'] == f'GET {_patient_path}'
        assert request_sent['status'] == ''

        # The stored document is the resubmit convention - payload plus the method, path and
        # query string a resend repeats.
        assert loads(request_sent['data']) == {'payload': '', 'method': 'get', 'path': _patient_path, 'params': {}}
        assert _get_attrs(request_sent['id']) == {'resource_type': 'Patient', 'method': 'GET'}

        response_received = events[1]

        assert response_received['source'] == AuditSource.FHIR
        assert response_received['event_type'] == AuditEvent.Response_Received
        assert response_received['outcome'] == AuditOutcome.OK
        assert response_received['cid'] == _cid
        assert response_received['status'] == f'{OK} OK'
        assert response_received['application_outcome'] == ''
        assert response_received['data'] == _patient_body
        assert response_received['size'] == len(_patient_body)

# ################################################################################################################################

def test_an_operation_outcome_on_500_carries_its_status_and_issue_code(tmp_path:'os.PathLike') -> 'None':
    """ A 500 answering an OperationOutcome is written with its whole status line and the code of its
    first issue, and the exception fhirpy raises for it is raised as fhirpy raises it.
    """
    body = operation_outcome('exception', 'The database is unavailable')

    with fhir_audit_env(tmp_path), FHIRStandIn(INTERNAL_SERVER_ERROR, body) as stand_in:

        client = new_fhir_client(stand_in.address)

        with pytest.raises(OperationOutcome):
            _ = client._do_request('get', _patient_path, cid=_cid)

        events = _get_events()
        assert len(events) == 2

        response_received = events[1]

        assert response_received['outcome'] == AuditOutcome.Error
        assert response_received['status'] == f'{INTERNAL_SERVER_ERROR} Internal Server Error'
        assert response_received['application_outcome'] == 'exception'
        assert response_received['data'] == body

# ################################################################################################################################

def test_a_404_carries_not_found_and_raises_resource_not_found(tmp_path:'os.PathLike') -> 'None':
    """ A 404 answering an OperationOutcome is written as `404 Not Found` with `not-found`,
    and it is ResourceNotFound that reaches the caller.
    """
    body = operation_outcome('not-found', 'No Patient with id 1')

    with fhir_audit_env(tmp_path), FHIRStandIn(NOT_FOUND, body) as stand_in:

        client = new_fhir_client(stand_in.address)

        with pytest.raises(ResourceNotFound):
            _ = client._do_request('get', _patient_path, cid=_cid)

        response_received = _get_events()[1]

        assert response_received['outcome'] == AuditOutcome.Error
        assert response_received['status'] == f'{NOT_FOUND} Not Found'
        assert response_received['application_outcome'] == 'not-found'

# ################################################################################################################################

def test_a_401_raises_authorization_error(tmp_path:'os.PathLike') -> 'None':
    """ A 401 is written as `401 Unauthorized` and raises AuthorizationError, a body that is not an
    OperationOutcome leaving the application outcome empty.
    """
    body = 'Access denied'

    with fhir_audit_env(tmp_path), FHIRStandIn(UNAUTHORIZED, body) as stand_in:

        client = new_fhir_client(stand_in.address)

        with pytest.raises(AuthorizationError):
            _ = client._do_request('get', _patient_path, cid=_cid)

        response_received = _get_events()[1]

        assert response_received['outcome'] == AuditOutcome.Error
        assert response_received['status'] == f'{UNAUTHORIZED} Unauthorized'
        assert response_received['application_outcome'] == ''

# ################################################################################################################################

def test_a_refused_connection_is_written_as_connection_error(tmp_path:'os.PathLike') -> 'None':
    """ A call that nothing answered leaves a response row whose status names the transport failure,
    and the requests exception propagates as it always did.
    """
    with fhir_audit_env(tmp_path):

        client = new_fhir_client(unreached_address())

        with pytest.raises(RequestsConnectionError):
            _ = client._do_request('get', _patient_path, cid=_cid)

        events = _get_events()
        assert len(events) == 2

        response_received = events[1]

        assert response_received['event_type'] == AuditEvent.Response_Received
        assert response_received['outcome'] == AuditOutcome.Error
        assert response_received['status'] == TransportStatus.Connection_Error
        assert response_received['cid'] == _cid

# ################################################################################################################################

def test_a_timeout_is_written_as_timeout(tmp_path:'os.PathLike') -> 'None':
    """ A server that outlasts the client's patience leaves a response row whose status is `timeout`.
    """
    with fhir_audit_env(tmp_path), FHIRStandIn(OK, _patient_body, is_stalling=True) as stand_in:

        client = new_fhir_client(stand_in.address)

        with pytest.raises(RequestsTimeout):
            _ = client._do_request('get', _patient_path, cid=_cid)

        response_received = _get_events()[1]

        assert response_received['outcome'] == AuditOutcome.Error
        assert response_received['status'] == TransportStatus.Timeout

# ################################################################################################################################

def test_a_health_check_lands_under_its_own_source_with_the_audit_log_off(tmp_path:'os.PathLike') -> 'None':
    """ A health check's ping is written under the connection's health source even when the connection's
    own audit log is off, and the response comes back as it is for the check to read.
    """
    body = operation_outcome('exception', 'Not ready')

    with fhir_audit_env(tmp_path), FHIRStandIn(INTERNAL_SERVER_ERROR, body) as stand_in:

        client = new_fhir_client(stand_in.address, is_audit_log_active=False)
        response = client.zato_ping(_cid, is_health_check=True)

        assert not response.ok
        assert response.status_code == INTERNAL_SERVER_ERROR

        # The ping read the CapabilityStatement
        assert stand_in.requests[0][1] == _ping_path

        events = _get_events()
        assert len(events) == 2

        for event in events:
            assert event['source'] == AuditSource.FHIR_Health
            assert event['object_name'] == Connection_Name
            assert event['cid'] == _cid

        assert events[0]['endpoint'] == f'GET {_ping_path}'
        assert events[1]['status'] == f'{INTERNAL_SERVER_ERROR} Internal Server Error'
        assert events[1]['application_outcome'] == 'exception'

# ################################################################################################################################

def test_a_dashboard_ping_with_the_audit_log_off_writes_nothing(tmp_path:'os.PathLike') -> 'None':
    """ A ping that is not a health check is the connection's own traffic - with the audit log off it leaves nothing.
    """
    with fhir_audit_env(tmp_path), FHIRStandIn(OK, '{"resourceType":"CapabilityStatement"}') as stand_in:

        client = new_fhir_client(stand_in.address, is_audit_log_active=False)
        response = client.zato_ping(_cid)

        assert response.ok
        assert _get_events() == []

# ################################################################################################################################

def test_needs_audit_off_writes_nothing(tmp_path:'os.PathLike') -> 'None':
    """ A resubmit records its own rows, so the call it makes with needs_audit off leaves none of its own.
    """
    with fhir_audit_env(tmp_path), FHIRStandIn(OK, _patient_body) as stand_in:

        client = new_fhir_client(stand_in.address)
        result = cast_('strdict', client._do_request('get', _patient_path, needs_audit=False, cid=_cid))

        assert result['id'] == '1'
        assert _get_events() == []

# ################################################################################################################################
# ################################################################################################################################
