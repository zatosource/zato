# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit rows a SOAP client leaves behind one call - the request before the call either way, then the response
# recorded after it was parsed, so a fault is recorded by its code and a call that never got a response by what
# kind of failure it was, which is what the alerting collectors count.

# stdlib
import socket
from http.client import INTERNAL_SERVER_ERROR

# requests
from requests.exceptions import ConnectionError as RequestsConnectionError, ReadTimeout

# pytest
import pytest

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.audit_log.common import TransportStatus
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import Content_Type, FaultCode, SOAPException, SOAPFault, SOAPVersion
from zato.common.soap.envelope import build_envelope, attach_body, to_bytes
from zato.common.soap.message import SOAPMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# What the test server answers a faulting path with
_fault_reason = 'Backend unavailable'

# ################################################################################################################################

def _new_message() -> 'SOAPMessage':
    out = SOAPMessage()
    out.namespace = 'urn:orders'
    out.id = '1'
    return out

# ################################################################################################################################

def _record_audit(client:'SOAPClient') -> 'list':
    """ Plugs an audit callback into a client and returns the list every event lands in, as dicts of what was passed.
    """
    recorded = []

    def callback(cid:'any_', event:'any_', endpoint:'any_', outcome:'any_', data:'any_', status:'any_'='',
        method:'any_'='', application_outcome:'any_'='', address:'any_'='', redacted:'any_'=None,
        **kwargs:'any_'):
        recorded.append({
            'event': event,
            'endpoint': endpoint,
            'outcome': outcome,
            'data': data,
            'status': status,
            'method': method,
            'application_outcome': application_outcome,
            'address': address,
            'redacted': redacted,
        })

    client.audit_callback = callback
    return recorded

# ################################################################################################################################

def _closed_port() -> 'int':
    """ A loopback port nothing listens on - bound and released, so a connection to it is refused.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        _, out = sock.getsockname()

    return out

# ################################################################################################################################

def _assert_request_first(recorded:'list') -> 'None':
    """ The request row is the first one written, whole and OK, whatever the call came to.
    """
    assert len(recorded) == 2
    assert recorded[0]['event'] == AuditEvent.Request_Sent
    assert recorded[0]['outcome'] == AuditOutcome.OK
    assert recorded[1]['event'] == AuditEvent.Response_Received

# ################################################################################################################################
# ################################################################################################################################

class TestResponseRows:

    def test_a_fault_is_recorded_by_its_code_next_to_its_status(self, soap_server:'any_') -> 'None':
        soap_server.configure('/fault', respond_fault=(FaultCode.Receiver, _fault_reason))

        client = SOAPClient({'address': soap_server.url('/fault'), 'soap_version': SOAPVersion.V12})
        recorded = _record_audit(client)

        with pytest.raises(SOAPFault) as exception_info:
            _ = client.invoke('op', _new_message(), cid='cid-fault')

        client.close()

        _assert_request_first(recorded)
        response = recorded[1]

        # The test server answers a fault on 400 - the row carries the status and the code, and the raw envelope
        assert response['outcome'] == AuditOutcome.Error
        assert response['status'] == '400 Bad Request'
        assert response['application_outcome'] == FaultCode.Receiver
        assert _fault_reason.encode('utf-8') in response['data']

        # The fault itself learned the status it arrived with
        assert exception_info.value.http_status == 400

    def test_a_good_response_is_recorded_without_an_application_outcome(self, soap_server:'any_') -> 'None':
        soap_server.configure('/ok')

        client = SOAPClient({'address': soap_server.url('/ok'), 'soap_version': SOAPVersion.V12})
        recorded = _record_audit(client)

        _ = client.invoke('op', _new_message(), cid='cid-ok')
        client.close()

        _assert_request_first(recorded)
        response = recorded[1]

        assert response['outcome'] == AuditOutcome.OK
        assert response['status'] == '200 OK'
        assert response['application_outcome'] == ''

    def test_a_non_fault_envelope_on_an_error_status_is_recorded_by_its_status_alone(self, soap_server:'any_') -> 'None':
        envelope = build_envelope(SOAPVersion.V12)
        _ = attach_body(envelope, _new_message(), 'opResponse')
        soap_server.configure('/error-body',
            respond_raw=(INTERNAL_SERVER_ERROR, to_bytes(envelope), Content_Type[SOAPVersion.V12]))

        client = SOAPClient({'address': soap_server.url('/error-body'), 'soap_version': SOAPVersion.V12})
        recorded = _record_audit(client)

        with pytest.raises(SOAPException):
            _ = client.invoke('op', _new_message(), cid='cid-error-body')

        client.close()

        # The response arrived, so it is recorded - as a 500 that is not a fault
        _assert_request_first(recorded)
        response = recorded[1]

        assert response['outcome'] == AuditOutcome.Error
        assert response['status'] == '500 Internal Server Error'
        assert response['application_outcome'] == ''

# ################################################################################################################################
# ################################################################################################################################

class TestTransportFailureRows:

    def test_a_refused_connection_is_recorded_as_a_connection_error(self) -> 'None':
        client = SOAPClient({'address': f'http://127.0.0.1:{_closed_port()}/soap', 'soap_version': SOAPVersion.V12})
        recorded = _record_audit(client)

        with pytest.raises(RequestsConnectionError):
            _ = client.invoke('op', _new_message(), cid='cid-refused')

        client.close()

        _assert_request_first(recorded)
        response = recorded[1]

        assert response['outcome'] == AuditOutcome.Error
        assert response['status'] == TransportStatus.Connection_Error
        assert response['application_outcome'] == ''

    def test_a_timeout_is_recorded_as_a_timeout(self, soap_server:'any_') -> 'None':
        soap_server.configure('/slow', delay=1)

        client = SOAPClient({'address': soap_server.url('/slow'), 'soap_version': SOAPVersion.V12, 'timeout': 0.3})
        recorded = _record_audit(client)

        with pytest.raises(ReadTimeout):
            _ = client.invoke('op', _new_message(), cid='cid-timeout')

        client.close()

        _assert_request_first(recorded)
        response = recorded[1]

        assert response['outcome'] == AuditOutcome.Error
        assert response['status'] == TransportStatus.Timeout

# ################################################################################################################################
# ################################################################################################################################
