# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a test does with the server of a channel suite - it calls the channels over HTTP as a client of theirs does and
# talks to the test services both transports provide under the same names.

# stdlib
import os
import subprocess
import time
from base64 import b64encode
from dataclasses import dataclass, field
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# PyYAML
from yaml import safe_load as yaml_load

# Test support
from queue_delivery.channel.type_under_test import Channel_Keys, get_type_under_test
from queue_delivery.client import as_dict, get_client, wait_for_queue_empty
from queue_delivery.dlq import Discard_All_Messages, get_dlq, invoke
from queue_delivery.type_under_test import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, anylist, strdict

# ################################################################################################################################
# ################################################################################################################################

_default_wait_timeout_seconds = 30.0
_poll_interval_seconds = 0.1

# A client of a channel waits this long for its response, which is also what an intake test must stay under
Call_Timeout = 10.0

# The services both transports' suites provide ..
_set_behaviour_service = 'test.queue-delivery.channel.set-behaviour'
_get_received_service = 'test.queue-delivery.channel.get-received'
_clear_service = 'test.queue-delivery.channel.clear'
_get_counts_service = 'test.queue-delivery.channel.get-counts'

# .. and the server's own hot deployment, which is what a file written to the pickup directory goes through
_hot_deploy_service = 'zato.hot-deploy.create'

# A refusal count meaning that the target refuses everything until it is told otherwise
Refuse_Everything = -1

# The counting service lands in the pickup directory under this name, which a redeploy writes again
Counting_Pickup_Name = 'queue_delivery_channel_counting.py'

# How long an export of the server's configuration may take
_export_timeout = 180

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ChannelResponse:
    """ What a call to a channel came back with.
    """
    status:'int'
    headers:'strdict' = field(default_factory=dict)
    text:'str' = ''

    # When the call returned, so a scenario can compare it with what the service recorded
    returned_at:'float' = 0.0

# ################################################################################################################################
# ################################################################################################################################

def channel_url(key:'str', params:'strdict | None'=None) -> 'str':
    """ The address of a channel on the server the session fixture started, with a query string if there is one.
    """
    type_under_test = get_type_under_test()
    out = TestConfig.base_url + type_under_test.url_paths[key]

    if params:
        out = out + '?' + urlencode(params)

    return out

# ################################################################################################################################

def post(url:'str', body:'bytes', headers:'strdict') -> 'ChannelResponse':
    """ One POST to a channel - whatever status comes back is the response, not an error.
    """
    request = Request(url, data=body, method='POST')

    for name, value in headers.items():
        request.add_header(name, value)

    try:
        with urlopen(request, timeout=Call_Timeout) as response:
            status = response.status
            response_headers = dict(response.headers)
            text = response.read().decode('utf-8')

    except HTTPError as error:
        status = error.code
        response_headers = dict(error.headers)
        text = error.read().decode('utf-8')

    out = ChannelResponse(status, response_headers, text, time.monotonic())
    return out

# ################################################################################################################################

def content_type_of(response:'ChannelResponse') -> 'str':
    """ The Content-Type a response came with, without its parameters.
    """
    for name, value in response.headers.items():
        if name.lower() == 'content-type':
            out = value.split(';')[0].strip()
            return out

    raise AssertionError(f'No Content-Type among {response.headers}')

# ################################################################################################################################
# ################################################################################################################################

def set_behaviour(client:'AdminClient', refuse_count:'int') -> 'None':
    """ Tells the target how many of the coming invocations to refuse - what it recorded so far stays.
    """
    _ = client.invoke(_set_behaviour_service, {'refuse_count': refuse_count})

# ################################################################################################################################

def accept_all(client:'AdminClient') -> 'None':
    """ Tells the target to accept everything from now on.
    """
    set_behaviour(client, 0)

# ################################################################################################################################

def clear_received(client:'AdminClient') -> 'None':
    """ Forgets every invocation and every instantiation recorded so far, leaving the target accepting.
    """
    _ = client.invoke(_clear_service, {})

# ################################################################################################################################

def get_received(client:'AdminClient') -> 'anylist':
    """ Every invocation the target has seen since it was last cleared, oldest first.
    """
    response = client.invoke(_get_received_service, {})
    response = as_dict(response)

    out = response['invocations']
    return out

# ################################################################################################################################

def get_accepted(client:'AdminClient') -> 'anylist':
    """ The invocations the target accepted, oldest first.
    """
    out = []

    for invocation in get_received(client):
        if invocation['is_accepted']:
            out.append(invocation)

    return out

# ################################################################################################################################

def wait_for_received(client:'AdminClient', count:'int', timeout:'float'=_default_wait_timeout_seconds) -> 'anylist':
    """ Blocks until the target has seen at least that many invocations, then returns them all.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        out = get_received(client)

        if len(out) >= count:
            return out

        time.sleep(_poll_interval_seconds)

    out = get_received(client)
    return out

# ################################################################################################################################

def wait_for_accepted(client:'AdminClient', count:'int', timeout:'float'=_default_wait_timeout_seconds) -> 'anylist':
    """ Blocks until the target has accepted at least that many invocations, then returns the accepted ones.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        out = get_accepted(client)

        if len(out) >= count:
            return out

        time.sleep(_poll_interval_seconds)

    out = get_accepted(client)
    return out

# ################################################################################################################################

def get_counts(client:'AdminClient') -> 'anydict':
    """ How many times the counting service and the hooked service were instantiated since the last clear.
    """
    response = client.invoke(_get_counts_service, {})

    out = as_dict(response)
    return out

# ################################################################################################################################

def get_gaps(invocations:'anylist') -> 'list[float]':
    """ How long passed between each invocation and the one before it, in the order the target saw them.
    """
    out = []

    for index in range(1, len(invocations)):
        gap = invocations[index]['time'] - invocations[index - 1]['time']
        out.append(gap)

    return out

# ################################################################################################################################

def redeploy_counting(client:'AdminClient', source_path:'str') -> 'None':
    """ Replaces the counting service's module in the pickup directory with the source of another file,
    the way an upload from the Dashboard does it.
    """
    with open(source_path, 'rb') as source_file:
        source = source_file.read()

    payload = b64encode(source).decode('ascii')

    _ = client.invoke(_hot_deploy_service, {
        'payload': payload,
        'payload_name': Counting_Pickup_Name,
    })

# ################################################################################################################################
# ################################################################################################################################

def export_config() -> 'anydict':
    """ Exports the server's configuration through enmasse, the way a user does it, and returns what the file holds.
    """
    output_path = os.path.join(TestConfig.server_directory, 'export.yaml')

    environment = os.environ.copy()
    _ = environment.pop('COVERAGE_PROCESS_START', None)

    command = [
        TestConfig.zato_bin, 'enmasse', TestConfig.server_directory,
        '--export',
        '--output', output_path,
    ]

    result = subprocess.run(command, capture_output=True, text=True, timeout=_export_timeout, env=environment)

    if result.returncode != 0:
        raise Exception(f'enmasse export failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    with open(output_path) as output_file:
        out = yaml_load(output_file)

    return out

# ################################################################################################################################

def exported_by_name(exported:'anydict', object_type:'str') -> 'anydict':
    """ The exported definitions of one type, by name.
    """
    out = {}

    for item in exported[object_type]:
        out[item['name']] = item

    return out

# ################################################################################################################################
# ################################################################################################################################

def reset_before_test() -> 'None':
    """ Every test starts with a target that has recorded nothing and accepts everything.
    """
    client = get_client()
    clear_received(client)

# ################################################################################################################################

def reset_after_test() -> 'None':
    """ Every test leaves the target accepting, the queues drained and the DLQs empty.
    """
    client = get_client()
    clear_received(client)

    type_under_test = get_type_under_test()

    for key in Channel_Keys:
        channel_name = type_under_test.connections[key]
        queue = wait_for_queue_empty(client, channel_name)

        if queue['depth'] != 0 or queue['messages']:
            raise Exception(f'Queue of `{channel_name}` did not drain, depth {queue["depth"]}, messages {queue["messages"]}')

    for key in Channel_Keys:
        channel_name = type_under_test.connections[key]
        dlq = get_dlq(client, channel_name)

        if dlq['messages']:
            _ = invoke(client, Discard_All_Messages, {'sub_key': dlq['sub_key']})

# ################################################################################################################################
# ################################################################################################################################
