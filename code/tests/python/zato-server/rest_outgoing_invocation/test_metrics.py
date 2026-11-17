# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Metrics - the request counter labeled with the connection name, the status class and the error source,
# and the duration histogram labeled with the connection name, for responses and for transport errors.

# stdlib
from http.client import FOUND, NOT_FOUND, OK, SERVICE_UNAVAILABLE, TOO_MANY_REQUESTS

# pytest
import pytest

# prometheus_client
from prometheus_client import REGISTRY

# requests
from requests.exceptions import ChunkedEncodingError

# Zato
from zato.common.exception import BackendInvocationError
from zato.common.util import http_retry

# Test support
from endpoint import CloseMode, EndpointResponse
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint, UnresponsiveListener
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

_requests_total = 'zato_rest_outgoing_requests_total'
_duration_count = 'zato_rest_outgoing_request_duration_seconds_count'
_duration_sum   = 'zato_rest_outgoing_request_duration_seconds_sum'

# ################################################################################################################################
# ################################################################################################################################

def _get_connection_name(path:'str') -> 'str':
    """ Returns a connection name unique to the test, so the counters of one test are not shared with any other.
    """
    suffix = path.rsplit('/', 1)[1]

    out = f'test.metrics.{suffix}'
    return out

# ################################################################################################################################

def _get_sample(name:'str', labels:'dict[str, str]') -> 'float':
    """ Returns the value of one sample, or zero if nothing was recorded under its labels.
    """
    out = REGISTRY.get_sample_value(name, labels)

    if out is None:
        out = 0.0

    return out

# ################################################################################################################################

def _get_request_count(connection_name:'str', status_class:'str', error_source:'str') -> 'float':
    labels = {
        'connection_name': connection_name,
        'status_code': status_class,
        'error_source': error_source,
    }

    out = _get_sample(_requests_total, labels)
    return out

# ################################################################################################################################

def _get_duration_count(connection_name:'str') -> 'float':
    out = _get_sample(_duration_count, {'connection_name': connection_name})
    return out

# ################################################################################################################################

def _get_duration_sum(connection_name:'str') -> 'float':
    out = _get_sample(_duration_sum, {'connection_name': connection_name})
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize(('status', 'status_class', 'error_source'), [
    (OK, '2xx', 'none'),
    (FOUND, '3xx', 'none'),
    (NOT_FOUND, '4xx', 'gateway'),
    (SERVICE_UNAVAILABLE, '5xx', 'gateway'),
])
def test_response_metrics(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    status:'int',
    status_class:'str',
    error_source:'str',
    ) -> 'None':
    """ A response increments the counter under its status class and error source, and the duration histogram once.
    """
    connection_name = _get_connection_name(path)
    endpoint.set_response(path, EndpointResponse(status, delay=0.1))

    connection = new_connection(server, endpoint.http_base, path, name=connection_name)

    _ = connection.get(Test_CID)
    _ = connection.get(Test_CID)

    assert _get_request_count(connection_name, status_class, error_source) == 2
    assert _get_duration_count(connection_name) == 2
    assert _get_duration_sum(connection_name) >= 0.2

# ################################################################################################################################

def test_connection_error_metrics(server:'ServerStub', path:'str', unresponsive_listener:'UnresponsiveListener') -> 'None':
    """ A connection that times out increments the counter under the transport class and the timeout error source.
    """
    connection_name = _get_connection_name(path)
    connection = new_connection(server, unresponsive_listener.base, path, name=connection_name, timeout=0.5)

    with pytest.raises(BackendInvocationError):
        _ = connection.get(Test_CID)

    assert _get_request_count(connection_name, '0xx', 'timeout') == 1
    assert _get_duration_count(connection_name) == 1

# ################################################################################################################################

def test_reset_metrics(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection reset before the response increments the counter under the transport class and the connection error source.
    """
    connection_name = _get_connection_name(path)
    endpoint.set_response(path, EndpointResponse(close_mode=CloseMode.Reset_Before_Response))

    connection = new_connection(server, endpoint.http_base, path, name=connection_name)

    with pytest.raises(BackendInvocationError):
        _ = connection.get(Test_CID)

    assert _get_request_count(connection_name, '0xx', 'connection-error') == 1
    assert _get_duration_count(connection_name) == 1

# ################################################################################################################################

def test_tls_error_metrics(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A failed TLS verification increments the counter under the transport class and the TLS error source.
    """
    connection_name = _get_connection_name(path)

    connection = new_connection(
        server, endpoint.https_base, path, name=connection_name, ca_certs_path=endpoint.certificates.other_ca_path)

    with pytest.raises(BackendInvocationError):
        _ = connection.get(Test_CID)

    assert _get_request_count(connection_name, '0xx', 'tls-error') == 1

# ################################################################################################################################

def test_other_error_metrics(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A response cut during its body increments the counter under the transport class and the generic error source.
    """
    connection_name = _get_connection_name(path)
    endpoint.set_response(path, EndpointResponse(body='Customer list', close_mode=CloseMode.Reset_During_Response))

    connection = new_connection(server, endpoint.http_base, path, name=connection_name)

    with pytest.raises(ChunkedEncodingError):
        _ = connection.get(Test_CID)

    assert _get_request_count(connection_name, '0xx', 'error') == 1

# ################################################################################################################################

def test_retried_call_metrics(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    monkeypatch:'pytest.MonkeyPatch',
    ) -> 'None':
    """ Each response of a retried call is counted, and the connection errors that preceded the last attempt are not.
    """
    monkeypatch.setattr(http_retry, 'sleep', [].append)

    connection_name = _get_connection_name(path)
    endpoint.set_responses(path, [
        EndpointResponse(close_mode=CloseMode.Reset_Before_Response),
        EndpointResponse(TOO_MANY_REQUESTS),
        EndpointResponse(),
    ])

    connection = new_connection(server, endpoint.http_base, path, name=connection_name, max_retries=2)

    response = connection.get(Test_CID)

    assert response.status_code == OK
    assert _get_request_count(connection_name, '0xx', 'connection-error') == 0
    assert _get_request_count(connection_name, '4xx', 'gateway') == 1
    assert _get_request_count(connection_name, '2xx', 'none') == 1
    assert _get_duration_count(connection_name) == 2

# ################################################################################################################################
# ################################################################################################################################
