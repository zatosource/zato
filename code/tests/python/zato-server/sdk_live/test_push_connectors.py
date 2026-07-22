# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Test suite
from _test_util import create_definition, delete_definition, get_client, read_server_log, wait_for

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

_conn_name = 'My Feed'
_conn_type = 'outconn-feed'
_get_messages_service = 'demo.feed.get-messages'

# ################################################################################################################################
# ################################################################################################################################

class _TestState:
    """ State shared by the tests, which run in the order they are defined in.
    """
    conn_id = 0

# ################################################################################################################################
# ################################################################################################################################

def test_push_create_definition(zato_server:'stranydict') -> 'None':
    """ A definition of the subscribing type can be created - starting it subscribes right away.
    """
    push_state = zato_server['push_state']
    subscribe_count_before = push_state.subscribe_count

    _TestState.conn_id = create_definition(zato_server, _conn_name, _conn_type,
        host='127.0.0.1',
        port=zato_server['push_port'],
        topic='prices',
        service='demo.feed.recorder',
        topic_name='demo.feed.topic-recorder',
    )

    # on_started ran and subscribed (2.3).
    assert push_state.subscribe_count > subscribe_count_before

    log_content = read_server_log(zato_server)
    assert f'Feed `{_conn_name}` subscribed to `prices`' in log_content

# ################################################################################################################################

def test_push_messages_reach_services_and_topics(zato_server:'stranydict') -> 'None':
    """ A message the target pushes on its own reaches a service through the connector's
    self.invoke and a topic through its self.publish (6.8).
    """
    zato_server['push_state'].push('price-100')

    client = get_client(zato_server)

    # The message reached the recorder service through self.invoke ..
    def _was_invoked() -> 'bool':
        response = client.invoke(_get_messages_service, {})
        out = 'price-100' in response['invoked']
        return out

    _ = wait_for(_was_invoked, 'the pushed message to reach a service via self.invoke')

    # .. and the topic recorder received it through self.publish.
    def _was_published() -> 'bool':
        response = client.invoke(_get_messages_service, {})
        out = any('price-100' in item for item in response['topic'])
        return out

    _ = wait_for(_was_published, 'the pushed message to reach a topic via self.publish')

# ################################################################################################################################

def test_push_reconnect_resubscribes(zato_server:'stranydict') -> 'None':
    """ Killing and restarting the target makes the framework reconnect and re-run on_started,
    which resubscribes - and newly pushed messages flow again (4.3).
    """
    push_state = zato_server['push_state']
    subscribe_count_before = push_state.subscribe_count

    # Kill the target, dropping the feed's connection, and bring it back on the same port.
    port = zato_server['kill_target_server']('push')
    zato_server['restart_target_server']('push', port)

    # The framework noticed the loss, reconnected and resubscribed - the counter proves on_started re-ran.
    def _resubscribed() -> 'bool':
        out = push_state.subscribe_count > subscribe_count_before
        return out

    _ = wait_for(_resubscribed, 'the feed to resubscribe after the target restart')

    # Messages pushed after the reconnect reach services again.
    push_state.push('price-200')

    client = get_client(zato_server)

    def _was_invoked() -> 'bool':
        response = client.invoke(_get_messages_service, {})
        out = 'price-200' in response['invoked']
        return out

    _ = wait_for(_was_invoked, 'a message pushed after the reconnect to arrive')

# ################################################################################################################################

def test_push_delete_definition(zato_server:'stranydict') -> 'None':
    """ Deleting the definition closes the feed's connection.
    """
    delete_definition(zato_server, _TestState.conn_id)

    def _closed() -> 'bool':
        log_content = read_server_log(zato_server)
        out = f'Feed client closed for `{_conn_name}`' in log_content
        return out

    _ = wait_for(_closed, 'the feed client to be closed')

# ################################################################################################################################
# ################################################################################################################################
