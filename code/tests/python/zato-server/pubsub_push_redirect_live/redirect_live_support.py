# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the tests of redirected pushes through a running server use - the scenarios of the suite with their
# subscribers, topics and paths, the endpoints the server pushes to, and the publication and the given-up
# messages of each scenario.

# stdlib
import time
from http.client import TEMPORARY_REDIRECT
from json import loads
from typing import NamedTuple

# gevent
from gevent import sleep as gevent_sleep

# Zato
from zato.common.test.client import AdminClient
from zato.server.base.parallel.delivery_rest import Max_Push_Redirects

# Test support
from http_endpoint.endpoint import EndpointResponse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http_endpoint.endpoint import RecordedRequest, TestEndpoint
    from zato.common.typing_ import any_, anydict, strlist

    recorded_request_list = list[RecordedRequest]
    strendpointdict       = dict[str, TestEndpoint]

# ################################################################################################################################
# ################################################################################################################################

# The keys of the endpoints that the server pushes to
Loopback_First  = 'loopback-first'
Loopback_Second = 'loopback-second'
Remote_First    = 'remote-first'

# How many attempts each message is given - the first one and two retries, one second apart, before it is given up
Max_Retries      = 2
Retry_Sleep_Time = 1
Attempt_Count    = 1 + Max_Retries

# How many requests a loop of redirects sends in one attempt - the first push and each redirect followed
Loop_Request_Count = Max_Push_Redirects + 1

# The services through which the tests publish and read what the server keeps
_service_publish     = 'test.pubsub-rest.publish'
_service_sub_keys    = 'test.pubsub-rest.get-sub-keys'
_service_failed      = 'test.pubsub-rest.get-failed-messages'

# How long a test waits for what it expects, in seconds
_wait_timeout = 90.0

# How often a test checks what it waits for, in seconds
_poll_interval = 0.1

# How long a test waits after its deliveries for any further request that must not arrive, in seconds
_settle_time = 3.0

# The prefix of the names of the subscribers and topics of the scenarios
_name_prefix = 'test.redirect.'

# ################################################################################################################################
# ################################################################################################################################

class Scenario(NamedTuple):
    """ One scenario of the suite, with its own subscriber, topic and path, at the endpoint the server pushes to.
    """
    name: str
    endpoint_key: str
    is_tls: bool

# ################################################################################################################################

# The scenarios whose messages are delivered
Delivered_Scenarios = [
    Scenario('temporary-path', Loopback_First, False),
    Scenario('permanent-port', Loopback_First, False),
    Scenario('localhost-alias', Loopback_First, False),
    Scenario('http-to-https', Loopback_First, False),
    Scenario('chain-at-limit', Loopback_First, False),
]

# The scenarios whose messages are given up
Given_Up_Scenarios = [
    Scenario('moved-permanently', Loopback_First, False),
    Scenario('found', Loopback_First, False),
    Scenario('see-other', Loopback_First, False),
    Scenario('loop', Loopback_First, False),
    Scenario('chain-beyond-limit', Loopback_First, False),
    Scenario('https-to-http', Loopback_First, True),
    Scenario('remote-to-loopback', Remote_First, False),
    Scenario('loopback-to-remote', Loopback_First, False),
]

# The scenario whose target fails the first attempt
Retry_Scenario = Scenario('retry', Loopback_First, False)

# The scenarios whose log lines are read
Log_Scenarios = [
    Scenario('log-temporary', Loopback_First, False),
    Scenario('log-permanent', Loopback_First, False),
]

All_Scenarios = Delivered_Scenarios + Given_Up_Scenarios + [Retry_Scenario] + Log_Scenarios

# ################################################################################################################################
# ################################################################################################################################

class LiveConfig:
    """ What the setup of the suite gives its tests - the server, the endpoints and the publisher.
    """
    base_url = ''
    invoke_password = ''
    server_log_path = ''
    endpoints:'strendpointdict' = {}

# ################################################################################################################################
# ################################################################################################################################

def get_scenario_id(scenario:'Scenario') -> 'str':
    """ Returns the ID of the test of a scenario.
    """
    out = scenario.name
    return out

# ################################################################################################################################

def get_name(scenario:'Scenario') -> 'str':
    """ Returns the name of the subscriber and of the topic of a scenario.
    """
    out = _name_prefix + scenario.name
    return out

# ################################################################################################################################

def get_source_path(scenario:'Scenario') -> 'str':
    """ Returns the path that the server pushes the messages of a scenario to.
    """
    out = f'/redirect/{scenario.name}/source'
    return out

# ################################################################################################################################

def get_target_path(scenario:'Scenario') -> 'str':
    """ Returns the path that the source of a scenario redirects to.
    """
    out = f'/redirect/{scenario.name}/target'
    return out

# ################################################################################################################################

def get_chain_paths(scenario:'Scenario', redirect_count:'int') -> 'strlist':
    """ Returns the paths of a chain of redirects, the source first and the target last.
    """
    source_path = get_source_path(scenario)
    out:'strlist' = [source_path]

    for index in range(1, redirect_count):
        hop_path = f'/redirect/{scenario.name}/hop-{index}'
        out.append(hop_path)

    target_path = get_target_path(scenario)
    out.append(target_path)

    return out

# ################################################################################################################################

def get_endpoint(key:'str') -> 'TestEndpoint':
    """ Returns one of the endpoints that the server pushes to.
    """
    out = LiveConfig.endpoints[key]
    return out

# ################################################################################################################################

def get_source_base(scenario:'Scenario') -> 'str':
    """ Returns the address of the listener that the server pushes the messages of a scenario to.
    """
    endpoint = get_endpoint(scenario.endpoint_key)

    if scenario.is_tls:
        out = endpoint.https_base
    else:
        out = endpoint.http_base

    return out

# ################################################################################################################################

def redirect_to(location:'str', status:'int'=TEMPORARY_REDIRECT) -> 'EndpointResponse':
    """ Returns a response that redirects a push to the location with the status.
    """
    headers = [('Location', location)]

    out = EndpointResponse(status, headers=headers)
    return out

# ################################################################################################################################

def set_chain(endpoint:'TestEndpoint', paths:'strlist') -> 'None':
    """ Makes each path of the chain redirect to the next one, the last one accepting the push.
    """
    redirect_count = len(paths) - 1

    for index in range(redirect_count):
        current = paths[index]
        next_path = paths[index + 1]
        location = endpoint.http_base + next_path

        response = redirect_to(location)
        endpoint.set_responses(current, [response])

# ################################################################################################################################
# ################################################################################################################################

def _get_client() -> 'AdminClient':
    out = AdminClient(LiveConfig.base_url, LiveConfig.invoke_password)
    return out

# ################################################################################################################################

def publish(scenario:'Scenario', data:'any_') -> 'str':
    """ Publishes a message to the topic of a scenario, with the retry policy of the suite, and returns its msg_id.
    """
    client = _get_client()
    topic_name = get_name(scenario)

    response = client.invoke(_service_publish, {
        'topic_name': topic_name,
        'data': data,
        'max_retries': Max_Retries,
        'retry_sleep_time': Retry_Sleep_Time,
    })

    out = response['msg_id']
    return out

# ################################################################################################################################

def get_sub_key(scenario:'Scenario') -> 'str':
    """ Returns the subscription key of the subscriber of a scenario.
    """
    client = _get_client()
    name = get_name(scenario)

    response = client.invoke(_service_sub_keys)
    sub_keys = response['sub_keys']

    out = sub_keys[name]
    return out

# ################################################################################################################################

def get_failed_msg_ids(sub_key:'str') -> 'strlist':
    """ Returns the messages of a subscriber whose delivery the audit log records as given up.
    """
    client = _get_client()
    response = client.invoke(_service_failed, {'sub_key': sub_key})

    out = response['msg_ids']
    return out

# ################################################################################################################################
# ################################################################################################################################

def wait_for_requests(endpoint:'TestEndpoint', path:'str', count:'int') -> 'recorded_request_list':
    """ Waits until the endpoint received the given number of requests for the path, then waits for any further
    request to arrive, and returns all of them. The waits yield to the listeners of the endpoints.
    """
    started = time.monotonic()
    deadline = started + _wait_timeout

    while True:
        requests = endpoint.get_requests(path)
        request_count = len(requests)

        if request_count >= count:
            break

        if time.monotonic() > deadline:
            raise Exception(f'Expected {count} requests for `{path}`, received {request_count} in {_wait_timeout}s')

        gevent_sleep(_poll_interval)

    gevent_sleep(_settle_time)

    out = endpoint.get_requests(path)
    return out

# ################################################################################################################################

def wait_for_given_up(scenario:'Scenario', msg_id:'str') -> 'None':
    """ Waits until the audit log records the delivery of the message as given up, then waits for any further
    request to arrive. The waits yield to the listeners of the endpoints.
    """
    sub_key = get_sub_key(scenario)
    started = time.monotonic()
    deadline = started + _wait_timeout

    while True:
        failed_msg_ids = get_failed_msg_ids(sub_key)

        if msg_id in failed_msg_ids:
            break

        if time.monotonic() > deadline:
            raise Exception(f'Message `{msg_id}` of `{scenario.name}` not given up in {_wait_timeout}s')

        gevent_sleep(_poll_interval)

    gevent_sleep(_settle_time)

# ################################################################################################################################
# ################################################################################################################################

def get_envelope(request:'RecordedRequest') -> 'anydict':
    """ Returns the envelope of the message that a push request has as its body.
    """
    out = loads(request.body)
    return out

# ################################################################################################################################
# ################################################################################################################################
