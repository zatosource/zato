# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Redirected pushes that a running server gives up - each message is attempted as many times as its retry policy
# allows, the audit log records it as given up, and the target of the redirect receives nothing.

# stdlib
from http.client import FOUND, MOVED_PERMANENTLY, SEE_OTHER

# pytest
import pytest

# Zato
from zato.server.base.parallel.delivery_rest import Max_Push_Redirects

# Test support
from redirect_live_support import Attempt_Count, get_chain_paths, get_endpoint, get_scenario_id, get_source_path, \
    get_target_path, Given_Up_Scenarios, Loop_Request_Count, Loopback_First, publish, redirect_to, Remote_First, \
    set_chain, wait_for_given_up

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http_endpoint.endpoint import TestEndpoint
    from redirect_live_support import Scenario

    expectation_tuple = tuple[TestEndpoint, str, TestEndpoint, str, int]

# ################################################################################################################################
# ################################################################################################################################

def _set_status(scenario:'Scenario', status:'int') -> 'expectation_tuple':
    """ A redirect with a status other than 307 and 308 to another path of the same listener.
    """
    first = get_endpoint(Loopback_First)

    source_path = get_source_path(scenario)
    target_path = get_target_path(scenario)
    location = first.http_base + target_path

    response = redirect_to(location, status)
    first.set_responses(source_path, [response])

    out = first, source_path, first, target_path, Attempt_Count
    return out

# ################################################################################################################################

def _set_moved_permanently(scenario:'Scenario') -> 'expectation_tuple':
    out = _set_status(scenario, MOVED_PERMANENTLY)
    return out

def _set_found(scenario:'Scenario') -> 'expectation_tuple':
    out = _set_status(scenario, FOUND)
    return out

def _set_see_other(scenario:'Scenario') -> 'expectation_tuple':
    out = _set_status(scenario, SEE_OTHER)
    return out

# ################################################################################################################################

def _set_loop(scenario:'Scenario') -> 'expectation_tuple':
    """ A source that redirects to itself, which each attempt reaches once for the first push and once per redirect.
    """
    first = get_endpoint(Loopback_First)

    source_path = get_source_path(scenario)
    target_path = get_target_path(scenario)
    location = first.http_base + source_path

    response = redirect_to(location)
    first.set_responses(source_path, [response])

    source_count = Attempt_Count * Loop_Request_Count

    out = first, source_path, first, target_path, source_count
    return out

# ################################################################################################################################

def _set_chain_beyond_limit(scenario:'Scenario') -> 'expectation_tuple':
    """ A chain of one redirect more than the limit allows.
    """
    first = get_endpoint(Loopback_First)

    redirect_count = Max_Push_Redirects + 1
    paths = get_chain_paths(scenario, redirect_count)
    set_chain(first, paths)

    source_path = paths[0]
    target_path = paths[-1]

    out = first, source_path, first, target_path, Attempt_Count
    return out

# ################################################################################################################################

def _set_https_to_http(scenario:'Scenario') -> 'expectation_tuple':
    """ A redirect from the TLS listener to the plain HTTP listener.
    """
    first = get_endpoint(Loopback_First)

    source_path = get_source_path(scenario)
    target_path = get_target_path(scenario)
    location = first.http_base + target_path

    response = redirect_to(location)
    first.set_responses(source_path, [response])

    out = first, source_path, first, target_path, Attempt_Count
    return out

# ################################################################################################################################

def _set_across_scopes(source:'TestEndpoint', target:'TestEndpoint', scenario:'Scenario') -> 'expectation_tuple':
    """ A redirect from an endpoint of one network scope to an endpoint of another.
    """
    source_path = get_source_path(scenario)
    target_path = get_target_path(scenario)
    location = target.http_base + target_path

    response = redirect_to(location)
    source.set_responses(source_path, [response])

    out = source, source_path, target, target_path, Attempt_Count
    return out

# ################################################################################################################################

def _set_remote_to_loopback(scenario:'Scenario') -> 'expectation_tuple':
    remote = get_endpoint(Remote_First)
    loopback = get_endpoint(Loopback_First)

    out = _set_across_scopes(remote, loopback, scenario)
    return out

def _set_loopback_to_remote(scenario:'Scenario') -> 'expectation_tuple':
    loopback = get_endpoint(Loopback_First)
    remote = get_endpoint(Remote_First)

    out = _set_across_scopes(loopback, remote, scenario)
    return out

# ################################################################################################################################

_setters = {
    'moved-permanently': _set_moved_permanently,
    'found': _set_found,
    'see-other': _set_see_other,
    'loop': _set_loop,
    'chain-beyond-limit': _set_chain_beyond_limit,
    'https-to-http': _set_https_to_http,
    'remote-to-loopback': _set_remote_to_loopback,
    'loopback-to-remote': _set_loopback_to_remote,
}

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('scenario', Given_Up_Scenarios, ids=get_scenario_id)
def test_message_is_given_up(scenario:'Scenario') -> 'None':

    setter = _setters[scenario.name]
    source, source_path, target, target_path, expected_source_count = setter(scenario)

    data = f'Order 1 of Anna Miller, scenario {scenario.name}'
    msg_id = publish(scenario, data)

    wait_for_given_up(scenario, msg_id)

    # Each attempt reached the source ..
    source_requests = source.get_requests(source_path)
    source_count = len(source_requests)

    assert source_count == expected_source_count

    # .. and none reached the target.
    target_requests = target.get_requests(target_path)
    assert target_requests == []

# ################################################################################################################################
# ################################################################################################################################
