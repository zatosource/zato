# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.test.client import AdminClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strnone

# ################################################################################################################################
# ################################################################################################################################

# The topics the enmasse file declares, one pushing to a service and one to a REST endpoint,
# and the service the first of them pushes to.
Topic_Service = 'test.publish-retry.service'
Topic_REST = 'test.publish-retry.rest'
Target_Service = 'test.publish-retry.target'

# A refusal count meaning that the target refuses everything until it is told otherwise.
Refuse_Everything = -1

# The services that hot deployment put in the server.
_publish_service = 'test.publish-retry.publish'
_set_behaviour_service = 'test.publish-retry.set-behaviour'
_get_received_service = 'test.publish-retry.get-received'
_get_queue_service = 'test.publish-retry.get-queue'

# How long one wait for an expected outcome may take at most, in seconds, and how long one polling sleep is.
_default_wait_timeout_seconds = 60
_poll_interval_seconds = 0.1

# How much more than the policy's sleep a gap between two attempts may be - the policy's jitter is a fraction
# of the sleep and the slack covers the greenlet's own overhead.
Jitter_Fraction = PubSub.Delivery.Jitter_Percent / 100
Slack_Seconds = 0.5

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:
    """ What the tests need to know about the environment the session fixture built for them.
    """

    base_url = ''
    password = ''
    server_directory = ''

    # The target of the REST push subscription
    receiver: 'any_' = None

# ################################################################################################################################
# ################################################################################################################################

def get_client() -> 'AdminClient':
    """ A client for the server the session fixture started.
    """
    out = AdminClient(TestConfig.base_url, TestConfig.password)
    return out

# ################################################################################################################################

def publish(client:'AdminClient', topic_name:'str', data:'any_', **kwargs:'any_') -> 'anydict':
    """ Publishes one message from inside a service, with whatever retry settings and expiration are given,
    and returns the id the message was given along with the publishing service's correlation id.
    """
    request:'anydict' = {
        'topic_name': topic_name,
        'data': data,
    }
    request.update(kwargs)

    out = client.invoke(_publish_service, request)
    return out

# ################################################################################################################################

def set_behaviour(client:'AdminClient', refuse_count:'int') -> 'None':
    """ Tells the target service how many of the coming invocations to refuse, which also forgets
    the invocations it saw so far.
    """
    _ = client.invoke(_set_behaviour_service, {'refuse_count': refuse_count})

# ################################################################################################################################

def get_invocations(client:'AdminClient') -> 'anylist':
    """ Every invocation the target service has seen since its behaviour was last set.
    """
    response = client.invoke(_get_received_service, {})

    out = response['invocations']
    return out

# ################################################################################################################################

def wait_for_invocations(
    client:'AdminClient',
    expected_count:'int',
    timeout:'float'=_default_wait_timeout_seconds,
    ) -> 'anylist':
    """ Blocks until the target service has seen that many invocations, then returns all of them.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        out = get_invocations(client)

        if len(out) >= expected_count:
            return out

        time.sleep(_poll_interval_seconds)

    out = get_invocations(client)
    return out

# ################################################################################################################################

def get_gaps(invocations:'anylist') -> 'anylist':
    """ How long each invocation came after the one before it.
    """
    out:'anylist' = []
    previous_time = None

    for invocation in invocations:
        current_time = invocation['time']

        if previous_time is not None:
            gap = current_time - previous_time
            out.append(gap)

        previous_time = current_time

    return out

# ################################################################################################################################

def assert_gap_within(gap:'float', expected:'float') -> 'None':
    """ A gap between two attempts is what the policy's sleep says, give or take the jitter and the slack.
    """
    lower = expected - Slack_Seconds
    upper = expected + expected * Jitter_Fraction + Slack_Seconds

    assert lower <= gap <= upper, f'Gap {gap:.2f} not within {lower:.2f}..{upper:.2f} (expected {expected})'

# ################################################################################################################################

def get_queue_depth(client:'AdminClient', topic_name:'str') -> 'int':
    """ How many messages wait in the queues of one topic's push subscribers.
    """
    response = client.invoke(_get_queue_service, {'topic_name': topic_name})

    out = response['pending']
    return out

# ################################################################################################################################

def wait_for_empty_queue(
    client:'AdminClient',
    topic_name:'str',
    timeout:'float'=_default_wait_timeout_seconds,
    ) -> 'int':
    """ Blocks until nothing waits in one topic's push queues, then returns what does.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        out = get_queue_depth(client, topic_name)

        if not out:
            return out

        time.sleep(_poll_interval_seconds)

    out = get_queue_depth(client, topic_name)
    return out

# ################################################################################################################################

def get_audit_events(msg_id:'str', event_type:'strnone'=None) -> 'anylist':
    """ The events the audit log holds about one message, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.msg_id == msg_id)

    if event_type:
        query = query.where(event_table.c.event_type == event_type)

    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            event = dict(row._mapping)
            out.append(event)

    return out

# ################################################################################################################################

def wait_for_audit_events(
    msg_id:'str',
    event_type:'str',
    expected_count:'int',
    timeout:'float'=_default_wait_timeout_seconds,
    ) -> 'anylist':
    """ Blocks until that many events of one type are in the audit log about one message, then returns them.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        out = get_audit_events(msg_id, event_type)

        if len(out) >= expected_count:
            return out

        time.sleep(_poll_interval_seconds)

    out = get_audit_events(msg_id, event_type)
    return out

# ################################################################################################################################
# ################################################################################################################################
