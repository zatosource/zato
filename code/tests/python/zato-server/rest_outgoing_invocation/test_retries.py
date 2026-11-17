# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Retries - timeouts, connection errors and rate-limited responses retried according to the retry settings
# of a connection or of a call, with the sleeps between attempts read from the lines that the retry loop logs.

# stdlib
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR, NOT_FOUND, OK, SERVICE_UNAVAILABLE, TOO_MANY_REQUESTS

# pytest
import pytest

# Zato
from zato.common.audit_log.common import TransportStatus
from zato.common.exception import BackendInvocationError

# Test support
from endpoint import CloseMode, EndpointResponse
from support import get_retry_sleeps, new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The body of the response that ends a run of retries
_body = 'Response after retries'

# The retry settings of the connections, whose sleeps between attempts are as short as the settings allow
_sleep_time = 1
_multiplier = 2

# How long a Retry-After date lies in the future
_retry_after_date_seconds = 3

# ################################################################################################################################
# ################################################################################################################################

def _reset() -> 'EndpointResponse':
    out = EndpointResponse(close_mode=CloseMode.Reset_Before_Response)
    return out

# ################################################################################################################################

def _too_many_requests(retry_after:'str') -> 'EndpointResponse':
    out = EndpointResponse(TOO_MANY_REQUESTS, headers=[('Retry-After', retry_after)])
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_no_retries_by_default(endpoint:'TestEndpoint', server:'ServerStub', path:'str', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ A connection without retry settings makes one attempt only.
    """
    endpoint.set_responses(path, [_reset(), EndpointResponse(body=_body)])

    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status == TransportStatus.Connection_Error
    assert len(endpoint.get_requests(path)) == 1
    assert get_retry_sleeps(caplog) == []

# ################################################################################################################################

def test_connection_error_retried(endpoint:'TestEndpoint', server:'ServerStub', path:'str', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ A connection error is retried, each sleep longer than the previous one by the multiplier.
    """
    endpoint.set_responses(path, [_reset(), _reset(), EndpointResponse(body=_body)])

    connection = new_connection(server, endpoint.http_base, path, max_retries=2, retry_sleep_time=_sleep_time,
        retry_backoff_multiplier=_multiplier)

    response = connection.get(Test_CID)

    assert response.status_code == OK
    assert response.text == _body

    assert len(endpoint.get_requests(path)) == 3
    assert get_retry_sleeps(caplog) == [1, 2]

# ################################################################################################################################

def test_timeout_retried(endpoint:'TestEndpoint', server:'ServerStub', path:'str', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ A timeout is retried.
    """
    endpoint.set_responses(path, [EndpointResponse(delay=1.5), EndpointResponse(body=_body)])

    connection = new_connection(server, endpoint.http_base, path, timeout=1, max_retries=1, retry_sleep_time=_sleep_time)

    response = connection.get(Test_CID)

    assert response.status_code == OK
    assert response.text == _body

    assert len(endpoint.get_requests(path)) == 2
    assert get_retry_sleeps(caplog) == [1]

# ################################################################################################################################

def test_retries_exhausted(endpoint:'TestEndpoint', server:'ServerStub', path:'str', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ A connection error that persists through every retry is raised after the last attempt.
    """
    endpoint.set_response(path, _reset())

    connection = new_connection(server, endpoint.http_base, path, max_retries=2, retry_sleep_time=_sleep_time,
        retry_backoff_multiplier=_multiplier)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status == TransportStatus.Connection_Error
    assert len(endpoint.get_requests(path)) == 3
    assert get_retry_sleeps(caplog) == [1, 2]

# ################################################################################################################################

def test_retry_after_seconds(endpoint:'TestEndpoint', server:'ServerStub', path:'str', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ A rate-limited response with Retry-After in seconds is retried after that many seconds.
    """
    endpoint.set_responses(path, [_too_many_requests('1'), EndpointResponse(body=_body)])

    connection = new_connection(server, endpoint.http_base, path, max_retries=1, retry_sleep_time=_sleep_time + 1)

    response = connection.get(Test_CID)

    assert response.status_code == OK
    assert len(endpoint.get_requests(path)) == 2
    assert get_retry_sleeps(caplog) == [1]

# ################################################################################################################################

def test_retry_after_date(endpoint:'TestEndpoint', server:'ServerStub', path:'str', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ A rate-limited response with Retry-After as a date is retried once that date is reached.
    """
    retry_at = datetime.now(timezone.utc) + timedelta(seconds=_retry_after_date_seconds)
    retry_after = format_datetime(retry_at, usegmt=True)

    endpoint.set_responses(path, [_too_many_requests(retry_after), EndpointResponse(body=_body)])

    connection = new_connection(server, endpoint.http_base, path, max_retries=1)

    response = connection.get(Test_CID)

    assert response.status_code == OK
    assert len(endpoint.get_requests(path)) == 2

    sleeps = get_retry_sleeps(caplog)

    assert len(sleeps) == 1
    assert sleeps[0] >= _retry_after_date_seconds - 2
    assert sleeps[0] <= _retry_after_date_seconds

# ################################################################################################################################

def test_retry_after_beyond_budget(endpoint:'TestEndpoint', server:'ServerStub', path:'str', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ A rate-limited response asking for a longer wait than the remaining budget is returned without a retry.
    """
    endpoint.set_responses(path, [_too_many_requests('120'), EndpointResponse(body=_body)])

    connection = new_connection(server, endpoint.http_base, path, max_retries=3)

    response = connection.get(Test_CID)

    assert response.status_code == TOO_MANY_REQUESTS
    assert len(endpoint.get_requests(path)) == 1
    assert get_retry_sleeps(caplog) == []

# ################################################################################################################################

def test_rate_limited_retries_exhausted(endpoint:'TestEndpoint', server:'ServerStub', path:'str', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ A rate-limited response that persists through every retry is returned after the last attempt.
    """
    endpoint.set_response(path, EndpointResponse(TOO_MANY_REQUESTS))

    connection = new_connection(server, endpoint.http_base, path, max_retries=2, retry_sleep_time=_sleep_time,
        retry_backoff_multiplier=_multiplier)

    response = connection.get(Test_CID)

    assert response.status_code == TOO_MANY_REQUESTS
    assert len(endpoint.get_requests(path)) == 3
    assert get_retry_sleeps(caplog) == [1, 2]

# ################################################################################################################################

def test_backoff_threshold(endpoint:'TestEndpoint', server:'ServerStub', path:'str', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ The backoff threshold caps the total sleep time, ending the retries before max_retries is reached.
    """
    endpoint.set_response(path, _reset())

    connection = new_connection(
        server,
        endpoint.http_base,
        path,
        max_retries=10,
        retry_sleep_time=_sleep_time,
        retry_backoff_multiplier=_multiplier,
        retry_backoff_threshold=4,
    )

    with pytest.raises(BackendInvocationError):
        _ = connection.get(Test_CID)

    assert get_retry_sleeps(caplog) == [1, 2, 1]
    assert len(endpoint.get_requests(path)) == 4

# ################################################################################################################################

def test_call_overrides_connection(endpoint:'TestEndpoint', server:'ServerStub', path:'str', caplog:'pytest.LogCaptureFixture') -> 'None':
    """ Retry settings given in the call win over the settings of the connection.
    """
    endpoint.set_responses(path, [_reset(), _reset(), EndpointResponse(body=_body)])

    connection = new_connection(server, endpoint.http_base, path, max_retries=0, retry_sleep_time=5)

    response = connection.get(Test_CID, max_retries=2, retry_sleep_time=_sleep_time, retry_backoff_multiplier=_multiplier)

    assert response.status_code == OK
    assert len(endpoint.get_requests(path)) == 3
    assert get_retry_sleeps(caplog) == [1, 2]

# ################################################################################################################################

@pytest.mark.parametrize('status', [BAD_REQUEST, NOT_FOUND, INTERNAL_SERVER_ERROR, SERVICE_UNAVAILABLE])
def test_error_response_not_retried(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    caplog:'pytest.LogCaptureFixture',
    status:'int',
    ) -> 'None':
    """ A 4xx or 5xx response other than a rate-limited one is returned without a retry.
    """
    endpoint.set_responses(path, [EndpointResponse(status), EndpointResponse(body=_body)])

    connection = new_connection(server, endpoint.http_base, path, max_retries=3)

    response = connection.get(Test_CID)

    assert response.status_code == status
    assert len(endpoint.get_requests(path)) == 1
    assert get_retry_sleeps(caplog) == []

# ################################################################################################################################
# ################################################################################################################################
