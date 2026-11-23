# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A redirected push whose target fails the first attempt - the next attempt starts at the configured address again.

# stdlib
from http.client import PERMANENT_REDIRECT, SERVICE_UNAVAILABLE

# Test support
from http_endpoint.endpoint import EndpointResponse
from redirect_live_support import get_endpoint, get_envelope, get_source_path, get_target_path, Loopback_First, \
    Loopback_Second, publish, redirect_to, Retry_Scenario, wait_for_requests

# ################################################################################################################################
# ################################################################################################################################

def test_second_attempt_starts_at_the_configured_address() -> 'None':

    first = get_endpoint(Loopback_First)
    second = get_endpoint(Loopback_Second)

    source_path = get_source_path(Retry_Scenario)
    target_path = get_target_path(Retry_Scenario)
    location = second.http_base + target_path

    # The source moved permanently, and the target fails the first attempt and accepts the second one
    source_response = redirect_to(location, PERMANENT_REDIRECT)
    first.set_responses(source_path, [source_response])

    unavailable = EndpointResponse(SERVICE_UNAVAILABLE)
    accepted = EndpointResponse()
    second.set_responses(target_path, [unavailable, accepted])

    data = 'Order 1 of Maria Johnson, retried'
    msg_id = publish(Retry_Scenario, data)

    target_requests = wait_for_requests(second, target_path, 2)
    source_requests = first.get_requests(source_path)

    target_count = len(target_requests)
    source_count = len(source_requests)

    # Each attempt went to the configured address first ..
    assert source_count == 2
    assert target_count == 2

    # .. and the message was delivered once, by its second attempt.
    first_request, second_request = target_requests

    first_attempt = first_request.get_header('X-Zato-Delivery-Attempt')
    second_attempt = second_request.get_header('X-Zato-Delivery-Attempt')

    first_envelope = get_envelope(first_request)
    second_envelope = get_envelope(second_request)

    assert first_attempt == '1'
    assert second_attempt == '2'

    assert first_envelope['msg_id'] == msg_id
    assert second_envelope['msg_id'] == msg_id

# ################################################################################################################################
# ################################################################################################################################
