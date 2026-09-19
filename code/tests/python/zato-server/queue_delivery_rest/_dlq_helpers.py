# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a test does with the DLQ of a connection.

# stdlib
import time
from http.client import INTERNAL_SERVER_ERROR

# Test support
from _helpers import as_dict, Connections, get_client, send

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import any_, anydict, anylist
    from _receiver import RecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

_default_wait_timeout_seconds = 30.0
_poll_interval_seconds = 0.1

# The direct attempt and one retry
Attempts_Per_Round = 2

_get_dlq_service = 'test.queue-delivery.get-dlq'
_subscribe_topic_service = 'test.queue-delivery.subscribe-topic'
_get_topic_messages_service = 'test.queue-delivery.get-topic-messages'
_invoke_service = 'test.queue-delivery.invoke'

Retry_Message = 'zato.pubsub.dlq.retry-message'
Retry_All_Messages = 'zato.pubsub.dlq.retry-all-messages'
Forward_Message = 'zato.pubsub.dlq.forward-message'
Forward_All_Messages = 'zato.pubsub.dlq.forward-all-messages'
Discard_Message = 'zato.pubsub.dlq.discard-message'
Discard_All_Messages = 'zato.pubsub.dlq.discard-all-messages'
Get_Queue_List = 'zato.pubsub.outgoing.get-queue-list'

# The suite runs the rule itself, there is no scheduler
DLQ_Run = 'zato.pubsub.dlq.run'
Get_Job_By_Name = 'zato.scheduler.job.get-by-name'

Forward_Sub_Key = 'zato.test.queue-delivery.forwarded'

# ################################################################################################################################
# ################################################################################################################################

def get_dlq(client:'AdminClient', conn_name:'str') -> 'anydict':
    """ What a connection's DLQ holds.
    """
    request = {
        'conn_name': conn_name,
    }

    response = client.invoke(_get_dlq_service, request)

    out = as_dict(response)
    return out

# ################################################################################################################################

def wait_for_dlq_count(
    client:'AdminClient',
    conn_name:'str',
    expected_count:'int',
    timeout:'float'=_default_wait_timeout_seconds,
    ) -> 'anydict':
    """ Blocks until a connection's DLQ holds that many messages, then returns what it holds.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        out = get_dlq(client, conn_name)

        if len(out['messages']) == expected_count:
            return out

        time.sleep(_poll_interval_seconds)

    out = get_dlq(client, conn_name)
    return out

# ################################################################################################################################

def invoke(client:'AdminClient', service_name:'str', request:'anydict') -> 'any_':
    """ Invokes one of the server's own services with a request and returns what it answered.
    """
    envelope = {
        'service_name': service_name,
        'request': request,
    }

    response = client.invoke(_invoke_service, envelope)
    response = as_dict(response)

    out = response['response']
    return out

# ################################################################################################################################

def subscribe_topic(client:'AdminClient', topic_name:'str') -> 'None':
    """ Makes the test sub key receive whatever is published to a topic from now on.
    """
    request = {
        'topic_name': topic_name,
        'sub_key': Forward_Sub_Key,
    }

    _ = client.invoke(_subscribe_topic_service, request)

# ################################################################################################################################

def get_topic_messages(client:'AdminClient', topic_name:'str') -> 'anylist':
    """ What was published to a topic since the test sub key last read it, oldest first.
    """
    request = {
        'topic_name': topic_name,
        'sub_key': Forward_Sub_Key,
    }

    response = client.invoke(_get_topic_messages_service, request)
    response = as_dict(response)

    out = response['messages']
    return out

# ################################################################################################################################

def send_to_dlq(client:'AdminClient', conn_name:'str', receiver:'RecordingReceiver', data:'anydict') -> 'anydict':
    """ Sends one message the endpoint turns down until its attempts ran out and returns the DLQ message it became.
    """
    receiver.answer_next([INTERNAL_SERVER_ERROR] * Attempts_Per_Round)

    result = send(client, conn_name, data)
    assert result['is_in_queue'] is True

    dlq = wait_for_dlq_count(client, conn_name, 1)
    assert len(dlq['messages']) == 1, dlq

    out = dlq['messages'][0]
    return out

# ################################################################################################################################

def run_dlq_rule(client:'AdminClient') -> 'anydict':
    """ Runs the DLQ rule once.
    """
    response = invoke(client, DLQ_Run, {})

    out = response['counts']
    return out

# ################################################################################################################################

def discard_all_dlqs() -> 'None':
    """ Empties the DLQ of every connection.
    """
    client = get_client()

    for conn_name in Connections.values():
        dlq = get_dlq(client, conn_name)

        if dlq['messages']:
            _ = invoke(client, Discard_All_Messages, {'sub_key': dlq['sub_key']})

# ################################################################################################################################
# ################################################################################################################################
