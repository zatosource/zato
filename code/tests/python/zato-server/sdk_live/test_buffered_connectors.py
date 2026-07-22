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

_conn_name = 'My Audit'
_conn_type = 'outconn-audit'
_service_name = 'demo.audit.send-event'

# How long the flush interval is once the flush-on-stop scenario begins - long enough
# that only on_stop can be what flushes the remaining events.
_long_flush_interval = 3600

# ################################################################################################################################
# ################################################################################################################################

class _TestState:
    """ State shared by the tests, which run in the order they are defined in.
    """
    conn_id = 0

# ################################################################################################################################
# ################################################################################################################################

def _send_event(zato_server:'stranydict', event:'str') -> 'None':
    client = get_client(zato_server)
    response = client.invoke(_service_name, {'event': event})
    assert response['response'] == 'sent'

# ################################################################################################################################

def _wait_for_received(zato_server:'stranydict', event:'str') -> 'None':
    counting_state = zato_server['counting_state']

    def _received() -> 'bool':
        with counting_state.lock:
            out = event in counting_state.received
        return out

    _ = wait_for(_received, f'the collector to receive {event}')

# ################################################################################################################################
# ################################################################################################################################

def test_buffered_create_definition(zato_server:'stranydict') -> 'None':
    """ A definition of the fire-and-forget type can be created and pinged.
    """
    _TestState.conn_id = create_definition(zato_server, _conn_name, _conn_type,
        host='127.0.0.1',
        port=zato_server['counting_port'],
        flush_interval=1,
    )

# ################################################################################################################################

def test_buffered_events_flush_in_batches(zato_server:'stranydict') -> 'None':
    """ Fire-and-forget events are buffered client-side and reach the collector
    with the next periodic flush.
    """
    _send_event(zato_server, 'event-1')
    _send_event(zato_server, 'event-2')

    _wait_for_received(zato_server, 'event-1')
    _wait_for_received(zato_server, 'event-2')

# ################################################################################################################################

def test_buffered_delete_flushes_remainder(zato_server:'stranydict') -> 'None':
    """ With flushing effectively off, deleting the definition is what delivers
    the buffered remainder - proving on_stop flushed (2.4).
    """
    client = get_client(zato_server)

    # Editing the definition swaps in a client whose periodic flush never comes.
    _ = client.edit('zato.generic.connection.edit',
        id=_TestState.conn_id,
        cluster_id=1,
        name=_conn_name,
        type_=_conn_type,
        is_active=True,
        is_internal=False,
        is_channel=False,
        is_outconn=True,
        host='127.0.0.1',
        port=zato_server['counting_port'],
        flush_interval=_long_flush_interval,
    )

    # The edit stopped the old client - from now on, events go to the new one,
    # whose periodic flush never comes.
    def _old_client_stopped() -> 'bool':
        log_content = read_server_log(zato_server)
        out = f'Audit client flushed and closed for `{_conn_name}`' in log_content
        return out

    _ = wait_for(_old_client_stopped, 'the edit to stop the old audit client')

    # These events stay in the buffer - nothing will flush them for an hour ..
    _send_event(zato_server, 'stop-1')
    _send_event(zato_server, 'stop-2')

    # .. so their delivery below proves that deleting the definition flushed them.
    delete_definition(zato_server, _TestState.conn_id)

    _wait_for_received(zato_server, 'stop-1')
    _wait_for_received(zato_server, 'stop-2')

# ################################################################################################################################
# ################################################################################################################################
