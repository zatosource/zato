# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Repeating one recorded REST or SOAP call out of what the row carries.

# stdlib
from http.client import OK

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditSource
from zato.common.destination.model import DestinationException
from zato.common.json_internal import loads
from zato.server.destination.dispatch import send_recorded

# Test support
from rest_stub import new_rest_wrapper, new_soap_wrapper, rest_audit_env, Address_Host, Connection_Name, ResponseStub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from zato.common.typing_ import any_, anylist, stranydict
    os = os
    any_ = any_
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The cid the original call ran under, and the one the repeat runs under
_cid = 'cid-rest-resend-original'
_resend_cid = 'cid-rest-resend-new'

# A connection whose address is built out of a path parameter, and the case one call was about
_templated_path = '/api/cases/{case_id}/notes'
_case_id = 'ABC-7'
_resolved_address = f'{Address_Host}/api/cases/{_case_id}/notes'

# What one call carries besides its body
_query_string = {'mode': 'full', 'lang': 'is'}
_caller_header = {'X-Zato-Case-Source': 'parking-form'}

# The body of a call, and what the endpoint answers with
_request_body = '{"note":"The car was towed"}'
_response_body = '{"result":"created"}'

# ################################################################################################################################
# ################################################################################################################################

class _Connections:
    """ What a repeat reaches for - one outgoing connection under each facade it may arrive by.
    """

    def __init__(self, wrapper:'any_') -> 'None':
        invoker = _Invoker(wrapper)

        self.rest = {Connection_Name: invoker}
        self.soap = {Connection_Name: invoker}
        self.fhir = {}
        self.mllp = {}
        self.email = {}

# ################################################################################################################################

class _Invoker:
    """ What a service holds for one outgoing connection - the wrapper behind it is what a
    repeat calls.
    """

    def __init__(self, wrapper:'any_') -> 'None':
        self.conn = wrapper

# ################################################################################################################################

def _recording_invoke_http(calls:'anylist') -> 'any_':
    """ An invoke_http stand-in that records every call it was made with and answers each
    of them with the same good response.
    """
    def invoke_http(cid:'any_', method:'any_', address:'any_', data:'any_', headers:'any_', hooks:'any_',
        *args:'any_', **kwargs:'any_') -> 'ResponseStub':
        calls.append({'method': method, 'address': address, 'data': data, 'headers': headers, 'kwargs': kwargs})
        return ResponseStub(OK, 'OK', _response_body)

    return invoke_http

# ################################################################################################################################

def _get_stored_call() -> 'stranydict':
    """ The document the newest request-sent row of the log carries.
    """
    engine = get_audit_engine()

    query = select(event_table.c.data)
    query = query.where(event_table.c.event_type == AuditEvent.Request_Sent)
    query = query.order_by(event_table.c.id.desc())

    with engine.connect() as connection:
        row = connection.execute(query).first()

    out = loads(row[0])
    return out

# ################################################################################################################################

def _resend(wrapper:'any_', details:'stranydict', source:'str'=AuditSource.REST_Outgoing) -> 'any_':
    """ Repeats one recorded call the way the Resubmit button does.
    """
    out = send_recorded(_Connections(wrapper), source, Connection_Name, details, details['payload'], _resend_cid)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_templated_address_is_repeated_as_it_resolved(tmp_path:'os.PathLike') -> 'None':
    """ The row keeps the address the call resolved to, so the repeat reaches the same case.
    """
    with rest_audit_env(tmp_path):

        calls:'anylist' = []

        wrapper = new_rest_wrapper(url_path=_templated_path)
        wrapper.invoke_http = _recording_invoke_http(calls)

        _ = wrapper.post(_cid, _request_body, params={'case_id': _case_id})

        details = _get_stored_call()
        assert details['address'] == _resolved_address

        calls.clear()
        _ = _resend(wrapper, details)

        assert len(calls) == 1

        call = calls[0]
        assert call['address'] == _resolved_address
        assert call['method'] == 'POST'
        assert call['data'] == _request_body.encode('utf-8')

# ################################################################################################################################

def test_the_query_string_goes_out_again_as_it_went_out(tmp_path:'os.PathLike') -> 'None':
    """ Parameters that did not fill the path became the query string, and the repeat carries it.
    """
    with rest_audit_env(tmp_path):

        calls:'anylist' = []

        wrapper = new_rest_wrapper()
        wrapper.invoke_http = _recording_invoke_http(calls)

        _ = wrapper.get(_cid, params=_query_string)

        details = _get_stored_call()
        assert details['params'] == _query_string

        calls.clear()
        _ = _resend(wrapper, details)

        assert len(calls) == 1

        call_kwargs = calls[0]['kwargs']
        assert call_kwargs['params'] == _query_string

# ################################################################################################################################

def test_a_caller_header_goes_out_again(tmp_path:'os.PathLike') -> 'None':
    """ A header the caller added is part of the call, so the repeat carries it too.
    """
    with rest_audit_env(tmp_path):

        calls:'anylist' = []

        wrapper = new_rest_wrapper()
        wrapper.invoke_http = _recording_invoke_http(calls)

        _ = wrapper.post(_cid, _request_body, headers=dict(_caller_header))

        details = _get_stored_call()
        assert details['headers'] == _caller_header

        calls.clear()
        _ = _resend(wrapper, details)

        assert len(calls) == 1

        call_headers = calls[0]['headers']

        for name, value in _caller_header.items():
            assert call_headers[name] == value

# ################################################################################################################################

def test_a_row_from_before_the_address_was_stored_is_refused(tmp_path:'os.PathLike') -> 'None':
    """ A row that stored the body and the method alone leaves a templated address with nothing
    to rebuild the call out of, so the repeat says so and stops.
    """
    with rest_audit_env(tmp_path):

        calls:'anylist' = []

        wrapper = new_rest_wrapper(url_path=_templated_path)
        wrapper.invoke_http = _recording_invoke_http(calls)

        bodyless_context = {'payload': _request_body, 'method': 'POST'}

        with pytest.raises(DestinationException) as raised:
            _ = _resend(wrapper, bodyless_context)

        assert 'templated address' in str(raised.value)
        assert 'predates stored request context' in str(raised.value)

        assert calls == []

# ################################################################################################################################

def test_a_row_from_before_the_address_was_stored_still_repeats_a_plain_call(tmp_path:'os.PathLike') -> 'None':
    """ A connection whose address is no template needs nothing rebuilt, so a row that stored
    neither address nor query string repeats all the same.
    """
    with rest_audit_env(tmp_path):

        calls:'anylist' = []

        wrapper = new_rest_wrapper()
        wrapper.invoke_http = _recording_invoke_http(calls)

        bodyless_context = {'payload': _request_body, 'method': 'POST'}

        _ = _resend(wrapper, bodyless_context)

        assert len(calls) == 1
        assert calls[0]['address'] == wrapper.address

# ################################################################################################################################

def test_a_soap_envelope_is_repeated_rather_than_wrapped_again(tmp_path:'os.PathLike') -> 'None':
    """ What a SOAP row carries is the envelope as it went on the wire, and the repeat sends it
    as it stands rather than wrapping it again.
    """
    with rest_audit_env(tmp_path):

        calls:'anylist' = []

        wrapper = new_soap_wrapper()
        wrapper.invoke_http = _recording_invoke_http(calls)

        _ = wrapper.post(_cid, '<GetCase><Id>7</Id></GetCase>')

        details = _get_stored_call()
        envelope = details['payload']

        assert envelope.count('Envelope') == 2

        calls.clear()
        _ = _resend(wrapper, details, AuditSource.SOAP_Outgoing)

        assert len(calls) == 1

        sent = calls[0]['data']

        if isinstance(sent, bytes):
            sent = sent.decode('utf-8')

        assert sent.count('Envelope') == 2

# ################################################################################################################################
# ################################################################################################################################
