# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import time

# pytest
import pytest

# Zato
from failover import Controller, create_container, docker, read_generation, run_container, wait_for_generation, \
    wait_until_up
from zato.common.test.client import PublishClient, PullClient
from zato.common.test.pubsub_database import connect

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FailoverEnvironment
    from failover import ContainerServer
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_failover')

# The topic of the tests, which has a pull subscriber and a push subscriber.
_topic_name = 'iam.user.created'

# How many messages each test publishes.
_message_count = 20

# How long the controller may take to switch the servers, in seconds.
_switch_timeout_seconds = 300

# How long a server may take to take over the database once its container started, in seconds.
_takeover_timeout_seconds = 180

# How long push deliveries may take to reach the receiver, in seconds.
_delivery_timeout_seconds = 120

# How often the tests check the receiver, in seconds.
_poll_seconds = 0.5

# How long a takeover may take beyond the startup of the server when a session blocks it, in seconds -
# five seconds of waiting, then the termination of the blocking session.
_blocked_takeover_max_seconds = 30

# ################################################################################################################################
# ################################################################################################################################

def _reset_pair(env:'FailoverEnvironment') -> 'int':
    """ Makes server A the active server and server B a stopped standby, and returns the current generation.
    """
    _ = docker('rm', '-f', env.server_b.container_name, check=False)
    run_container(env.server_a)
    _ = wait_until_up(env.server_a)
    create_container(env.server_b)

    out = read_generation(env.database)
    return out

# ################################################################################################################################

def _publisher(env:'FailoverEnvironment', server:'ContainerServer') -> 'PublishClient':
    out = PublishClient(server.base_url, env.publisher_username, env.publisher_password)
    return out

# ################################################################################################################################

def _puller(env:'FailoverEnvironment', server:'ContainerServer') -> 'PullClient':
    out = PullClient(server.base_url, env.puller_username, env.puller_password)
    return out

# ################################################################################################################################

def _publish(env:'FailoverEnvironment', server:'ContainerServer', count:'int') -> 'strlist':
    publisher = _publisher(env, server)
    out:'strlist' = []

    for index in range(count):
        result = publisher.publish(_topic_name, {'failover_test_index': index})
        out.append(result['msg_id'])

    return out

# ################################################################################################################################

def _pull_all(env:'FailoverEnvironment', server:'ContainerServer') -> 'strlist':
    """ Pulls everything pending for the pull subscriber through the given server and returns the identifiers.
    """
    puller = _puller(env, server)
    out:'strlist' = []

    while True:
        result = puller.pull(max_messages=100)
        if result['message_count'] == 0:
            break
        for message in result['messages']:
            out.append(message['meta']['msg_id'])

    return out

# ################################################################################################################################

def _wait_for_deliveries(receiver:'WebhookReceiver', msg_ids:'strlist') -> 'dictlist':
    """ Waits until the receiver has every one of the given messages and returns what it received.
    """
    deadline = time.monotonic() + _delivery_timeout_seconds
    expected = set(msg_ids)

    while True:

        delivered = receiver.get_delivered_messages()
        received:'set[str]' = set()

        for message in delivered:
            received.add(message['msg_id'])

        missing = expected - received

        if not missing:
            return delivered

        assert time.monotonic() < deadline, f'Not delivered: {sorted(missing)}'
        time.sleep(_poll_seconds)

# ################################################################################################################################

def _assert_repeats_have_higher_attempts(delivered:'dictlist') -> 'None':
    """ Every repeated copy of a message carries the same identifier with a higher attempt number.
    """
    attempts_by_msg_id:'dict[str, list[int]]' = {}

    for message in delivered:
        msg_id = message['msg_id']
        if msg_id not in attempts_by_msg_id:
            attempts_by_msg_id[msg_id] = []
        attempts_by_msg_id[msg_id].append(message['delivery_attempt'])

    for msg_id, attempts in attempts_by_msg_id.items():
        assert len(attempts) == len(set(attempts)), (msg_id, attempts)

# ################################################################################################################################
# ################################################################################################################################

def test_takeover_after_kill(failover_env:'FailoverEnvironment') -> 'None':
    """ The controller starts the standby once the active server is killed, the standby takes over the database,
    and every message published to the old server is pulled from and pushed by the new one.
    """
    env = failover_env
    generation = _reset_pair(env)

    receiver = env.receivers[_topic_name]
    receiver.clear_output()

    # The push subscriber is unavailable while the messages are published, so they wait in its queue ..
    receiver.stop()
    msg_ids = _publish(env, env.server_a, _message_count)

    # .. the active server is killed, and the controller notices it ..
    controller = Controller(env.server_a, env.server_b, os.path.join(env.work_dir, 'controller-kill.jsonl'))
    controller.start()

    kill_time = time.monotonic()
    _ = docker('kill', env.server_a.container_name)

    try:
        exit_code = controller.wait(_switch_timeout_seconds)
    finally:
        controller.stop()

    assert exit_code == 0, controller.read_events()

    events = controller.read_events()
    names:'strlist' = []

    for event in events:
        names.append(event['event'])

    assert 'standby_started' in names, events
    assert 'old_stopped' in names, events

    # .. the standby is up, with the next generation ..
    _ = wait_until_up(env.server_b)
    _ = wait_for_generation(env.database, generation + 1, _takeover_timeout_seconds)

    switch_seconds = time.monotonic() - kill_time
    logger.info('Kill to takeover: %.1fs', switch_seconds)

    # .. it hands out every message to the pull subscriber ..
    pulled = _pull_all(env, env.server_b)
    assert sorted(pulled) == sorted(msg_ids)

    # .. and pushes every one of them once the push subscriber returns.
    receiver.restart()

    delivered = _wait_for_deliveries(receiver, msg_ids)
    _assert_repeats_have_higher_attempts(delivered)

# ################################################################################################################################

def test_replaced_server_rejected(failover_env:'FailoverEnvironment') -> 'None':
    """ A server whose generation was replaced while it kept running publishes, hands out and changes nothing,
    and the server that replaced it serves everything.
    """
    env = failover_env
    generation = _reset_pair(env)

    # Server B starts while server A is still running, as it does when the controller loses sight of server A ..
    _ = docker('start', env.server_b.container_name)
    _ = wait_until_up(env.server_b)
    _ = wait_for_generation(env.database, generation + 1, _takeover_timeout_seconds)

    # .. server A rejects every publication ..
    with pytest.raises(Exception, match='HTTP'):
        _ = _publish(env, env.server_a, 1)

    # .. server B accepts them ..
    msg_ids = _publish(env, env.server_b, 5)

    # .. server A hands out nothing ..
    with pytest.raises(Exception, match='HTTP'):
        _ = _puller(env, env.server_a).pull(max_messages=100)

    # .. so server B hands out everything.
    pulled = _pull_all(env, env.server_b)
    assert sorted(pulled) == sorted(msg_ids)

    _ = docker('stop', '--time', '10', env.server_a.container_name)

# ################################################################################################################################

def test_takeover_from_open_session(failover_env:'FailoverEnvironment') -> 'None':
    """ A session that holds the row of the generation open does not keep the standby from taking over,
    which terminates the session after it waited for it.
    """
    env = failover_env
    generation = _reset_pair(env)

    # A session locks the row of the generation and stays open ..
    blocker = connect(env.database)
    cursor = blocker.cursor()
    cursor.execute('select generation from pubsub_active where id = 1 for share')

    # .. the standby is started ..
    start = time.monotonic()
    _ = docker('start', env.server_b.container_name)

    startup_seconds = wait_until_up(env.server_b)
    _ = wait_for_generation(env.database, generation + 1, _takeover_timeout_seconds)

    takeover_seconds = time.monotonic() - start
    logger.info('Startup %.1fs, takeover %.1fs', startup_seconds, takeover_seconds)

    assert takeover_seconds < startup_seconds + _blocked_takeover_max_seconds, (startup_seconds, takeover_seconds)

    # .. and the session was terminated.
    with pytest.raises(Exception):
        cursor.execute('select 1')

    _ = docker('stop', '--time', '10', env.server_a.container_name)

# ################################################################################################################################
# ################################################################################################################################
