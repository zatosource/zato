# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Redirected pushes that a running server delivers - each message reaches the target of its redirects once,
# with its envelope as the body and with its identifier and attempt in the headers.

# stdlib
from http.client import PERMANENT_REDIRECT

# pytest
import pytest

# Zato
from zato.server.base.parallel.delivery_rest import Max_Push_Redirects

# Test support
from redirect_live_support import Delivered_Scenarios, get_chain_paths, get_endpoint, get_envelope, get_scenario_id, \
    get_source_path, get_target_path, Loopback_First, Loopback_Second, publish, redirect_to, set_chain, wait_for_requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http_endpoint.endpoint import TestEndpoint
    from redirect_live_support import Scenario
    from zato.common.typing_ import strlist, strstrdict

    target_tuple = tuple[TestEndpoint, str]

# ################################################################################################################################
# ################################################################################################################################

# How many messages each scenario publishes
_message_count = 3

# ################################################################################################################################
# ################################################################################################################################

def _set_temporary_path(scenario:'Scenario') -> 'target_tuple':
    """ A 307 to another path of the same listener.
    """
    first = get_endpoint(Loopback_First)
    target_path = get_target_path(scenario)

    source_path = get_source_path(scenario)
    location = first.http_base + target_path

    response = redirect_to(location)
    first.set_responses(source_path, [response])

    out = first, target_path
    return out

# ################################################################################################################################

def _set_permanent_port(scenario:'Scenario') -> 'target_tuple':
    """ A 308 to a listener on another port.
    """
    first = get_endpoint(Loopback_First)
    second = get_endpoint(Loopback_Second)
    target_path = get_target_path(scenario)

    source_path = get_source_path(scenario)
    location = second.http_base + target_path

    response = redirect_to(location, PERMANENT_REDIRECT)
    first.set_responses(source_path, [response])

    out = second, target_path
    return out

# ################################################################################################################################

def _set_localhost_alias(scenario:'Scenario') -> 'target_tuple':
    """ A 307 to the same listener under the localhost alias.
    """
    first = get_endpoint(Loopback_First)
    target_path = get_target_path(scenario)

    source_path = get_source_path(scenario)
    location = f'http://localhost:{first.http_port}{target_path}'

    response = redirect_to(location)
    first.set_responses(source_path, [response])

    out = first, target_path
    return out

# ################################################################################################################################

def _set_http_to_https(scenario:'Scenario') -> 'target_tuple':
    """ A 307 from the plain HTTP listener to the TLS listener.
    """
    first = get_endpoint(Loopback_First)
    target_path = get_target_path(scenario)

    source_path = get_source_path(scenario)
    location = first.https_base + target_path

    response = redirect_to(location)
    first.set_responses(source_path, [response])

    out = first, target_path
    return out

# ################################################################################################################################

def _set_chain_at_limit(scenario:'Scenario') -> 'target_tuple':
    """ A chain of as many redirects as the limit allows.
    """
    first = get_endpoint(Loopback_First)

    paths = get_chain_paths(scenario, Max_Push_Redirects)
    set_chain(first, paths)

    target_path = paths[-1]

    out = first, target_path
    return out

# ################################################################################################################################

_setters = {
    'temporary-path': _set_temporary_path,
    'permanent-port': _set_permanent_port,
    'localhost-alias': _set_localhost_alias,
    'http-to-https': _set_http_to_https,
    'chain-at-limit': _set_chain_at_limit,
}

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('scenario', Delivered_Scenarios, ids=get_scenario_id)
def test_each_message_is_delivered_once(scenario:'Scenario') -> 'None':

    setter = _setters[scenario.name]
    target, target_path = setter(scenario)

    published:'strstrdict' = {}

    for index in range(_message_count):
        data = f'Order {index} of John Smith, scenario {scenario.name}'
        msg_id = publish(scenario, data)
        published[msg_id] = data

    requests = wait_for_requests(target, target_path, _message_count)

    # Each message arrived exactly once ..
    received_msg_ids:'strlist' = []

    for request in requests:

        envelope = get_envelope(request)
        msg_id = envelope['msg_id']
        received_msg_ids.append(msg_id)

        # .. with its envelope as the body and its identifier and its first attempt in the headers.
        header_msg_id = request.get_header('X-Zato-Msg-ID')
        header_attempt = request.get_header('X-Zato-Delivery-Attempt')

        assert request.method == 'POST'
        assert header_msg_id == msg_id
        assert header_attempt == '1'
        assert envelope['data'] == published[msg_id]

    published_msg_ids = list(published)

    assert sorted(received_msg_ids) == sorted(published_msg_ids)

# ################################################################################################################################
# ################################################################################################################################
