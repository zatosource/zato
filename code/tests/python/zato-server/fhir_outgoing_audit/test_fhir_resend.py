# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Repeating one recorded FHIR call out of the method, the path and the query string the row carries.

# stdlib
from http.client import BAD_REQUEST, OK
from urllib.parse import parse_qs, urlparse

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditSource
from zato.common.destination.audit import get_hop_entry
from zato.common.destination.constants import DestinationOption
from zato.common.json_internal import loads
from zato.common.typing_ import cast_
from zato.server.destination.dispatch import _send_fhir

# Test support
from fhir_stub import fhir_audit_env, new_fhir_client, operation_outcome, Connection_Name, FHIRStandIn

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from zato.common.typing_ import any_, stranydict
    os = os
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The cid the original call ran under
_cid = 'cid-fhir-resend-1'

# The resource a read and a delete are about
_patient_path = 'Patient/1'

# What a good read answers with
_patient_body = '{"resourceType":"Patient","id":"1"}'

# What a good delete answers with
_deleted_body = '{"resourceType":"OperationOutcome","issue":[]}'

# The search one call runs, and what it answers with
_search_path = 'Observation'
_search_params = {'patient': '1', 'code': 'http://loinc.org|1975-2'}
_search_body = '{"resourceType":"Bundle","total":0}'

# ################################################################################################################################
# ################################################################################################################################

class _Connections:
    """ What the adapter reaches for - the one FHIR client under test.
    """

    def __init__(self, client:'any_') -> 'None':
        self.fhir = {Connection_Name: client}
        self.rest = {}
        self.soap = {}
        self.mllp = {}
        self.email = {}

# ################################################################################################################################

def _get_stored_call() -> 'stranydict':
    """ The document the one request-sent row of the log carries.
    """
    engine = get_audit_engine()

    query = select(event_table.c.data)
    query = query.where(event_table.c.event_type == AuditEvent.Request_Sent)
    query = query.order_by(event_table.c.id)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    assert len(rows) == 1

    row = rows[0]
    out = loads(row[0])

    return out

# ################################################################################################################################

def _resend(client:'any_') -> 'any_':
    """ Turns the recorded call back into its destination and makes it again, the way the
    Resubmit button does.
    """
    details = _get_stored_call()

    entry = get_hop_entry(AuditSource.FHIR, Connection_Name, details)

    out = _send_fhir(cast_('any_', _Connections(client)), entry, details['payload'])
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_read_goes_out_again_with_no_body(tmp_path:'os.PathLike') -> 'None':
    """ A GET recorded an empty payload, and repeating it asks the same question again.
    """
    with fhir_audit_env(tmp_path), FHIRStandIn(OK, _patient_body) as stand_in:

        client = new_fhir_client(stand_in.address)
        _ = client._do_request('get', _patient_path, cid=_cid)

        stand_in.requests = []

        result = _resend(client)

        assert len(stand_in.requests) == 1

        method, path, body = stand_in.requests[0]

        assert method == 'GET'
        assert path == f'/{_patient_path}'
        assert body == ''

        assert result.is_rejected is False
        assert result.response['resourceType'] == 'Patient'

# ################################################################################################################################

def test_a_delete_goes_out_again_as_a_delete(tmp_path:'os.PathLike') -> 'None':
    """ The method is read back off the row, so a delete repeats as a delete.
    """
    with fhir_audit_env(tmp_path), FHIRStandIn(OK, _deleted_body) as stand_in:

        client = new_fhir_client(stand_in.address)
        _ = client._do_request('delete', _patient_path, cid=_cid)

        stand_in.requests = []

        _ = _resend(client)

        assert len(stand_in.requests) == 1

        method, path, body = stand_in.requests[0]

        assert method == 'DELETE'
        assert path == f'/{_patient_path}'
        assert body == ''

# ################################################################################################################################

def test_a_search_goes_out_again_with_its_parameters(tmp_path:'os.PathLike') -> 'None':
    """ A search is its parameters, so the repeat searches by the same ones.
    """
    with fhir_audit_env(tmp_path), FHIRStandIn(OK, _search_body) as stand_in:

        client = new_fhir_client(stand_in.address)
        _ = client._do_request('get', _search_path, params=_search_params, cid=_cid)

        # The row keeps them, so the resend has them to work with.
        assert _get_stored_call()[DestinationOption.Params] == _search_params

        stand_in.requests = []

        _ = _resend(client)

        assert len(stand_in.requests) == 1

        method, path, _ = stand_in.requests[0]
        parsed = urlparse(path)

        assert method == 'GET'
        assert parsed.path == f'/{_search_path}'
        assert parse_qs(parsed.query) == {'patient': ['1'], 'code': ['http://loinc.org|1975-2']}

# ################################################################################################################################

def test_a_refused_resend_carries_the_status_it_was_refused_with(tmp_path:'os.PathLike') -> 'None':
    """ A resend a server refused comes back rejected, naming the status and what the server said.
    """
    outcome_body = operation_outcome('invalid', 'The patient id is not a number')

    with fhir_audit_env(tmp_path), FHIRStandIn(OK, _patient_body) as stand_in:

        client = new_fhir_client(stand_in.address)
        _ = client._do_request('get', _patient_path, cid=_cid)

        # The same call refused the second time round.
        stand_in.status = BAD_REQUEST
        stand_in.body = outcome_body

        result = _resend(client)

        assert result.is_rejected is True
        assert result.status == f'HTTP {BAD_REQUEST} Bad Request'
        assert result.response_text == outcome_body

        issues = result.response['issue']
        assert issues[0]['diagnostics'] == 'The patient id is not a number'

# ################################################################################################################################
# ################################################################################################################################
