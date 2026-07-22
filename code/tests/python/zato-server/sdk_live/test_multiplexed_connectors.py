# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading

# Test suite
from _test_util import create_definition, delete_definition, get_client, wait_for

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

_conn_name = 'My Payments'
_conn_type = 'outconn-payments'
_service_name = 'demo.payments.authorize'

# ################################################################################################################################
# ################################################################################################################################

class _TestState:
    """ State shared by the tests, which run in the order they are defined in.
    """
    conn_id = 0

# ################################################################################################################################
# ################################################################################################################################

def test_multiplexed_create_definition(zato_server:'stranydict') -> 'None':
    """ A definition of the multiplexed type can be created and pinged.
    """
    _TestState.conn_id = create_definition(zato_server, _conn_name, _conn_type,
        host='127.0.0.1',
        port=zato_server['correlation_port'],
    )

# ################################################################################################################################

def test_multiplexed_invoke(zato_server:'stranydict') -> 'None':
    """ A single request-reply round trip over the multiplexed socket.
    """
    client = get_client(zato_server)

    response = client.invoke(_service_name, {'payload': 'auth-1'})
    assert response['response'] == 'echo auth-1'

# ################################################################################################################################

def test_multiplexed_concurrent_out_of_order(zato_server:'stranydict') -> 'None':
    """ Concurrent in-flight invocations share one socket and each still gets its own reply,
    even though the slow request is answered after the fast ones - out of order.
    """

    correlation_state = zato_server['correlation_state']

    # How many connections the target saw before this test ran.
    with correlation_state.lock:
        connections_before = correlation_state.connection_count

    results = {}
    errors = []
    lock = threading.Lock()

    def _invoke(payload:'str') -> 'None':
        try:
            # Each thread needs its own client
            client = get_client(zato_server)
            response = client.invoke(_service_name, {'payload': payload})

            with lock:
                results[payload] = response['response']

        except Exception as e:
            with lock:
                errors.append(str(e))

    # The slow request goes out first and is answered last.
    payloads = ['slow first', 'quick-2', 'quick-3']
    threads = [threading.Thread(target=_invoke, args=(payload,)) for payload in payloads]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(60)

    assert not errors, f'Concurrent invocations failed: {errors}'

    # Each request got its own reply, correlated by ID and not by arrival order ..
    for payload in payloads:
        assert results[payload] == f'echo {payload}', f'Wrong reply for {payload}: {results}'

    # .. and all of them travelled over the socket that already existed - no new connections.
    with correlation_state.lock:
        connections_after = correlation_state.connection_count

    assert connections_after == connections_before, 'Concurrent requests were expected to share one socket'

# ################################################################################################################################

def test_multiplexed_drop_and_reconnect(zato_server:'stranydict') -> 'None':
    """ Dropping the connection makes the framework evict the client and the next
    invocation uses a new connection to the restarted target (7.4).
    """
    port = zato_server['kill_target_server']('correlation')
    zato_server['restart_target_server']('correlation', port)

    client = get_client(zato_server)

    # Validation before use notices the dead socket, the framework rebuilds the client
    # and the call goes through over the new connection.
    def _answers() -> 'bool':
        response = client.invoke(_service_name, {'payload': 'after-drop'})
        out = response['response'] == 'echo after-drop'
        return out

    _ = wait_for(_answers, 'the reconnected multiplexed connection to answer')

# ################################################################################################################################

def test_multiplexed_delete_definition(zato_server:'stranydict') -> 'None':
    """ Deleting the definition closes the multiplexed socket.
    """
    delete_definition(zato_server, _TestState.conn_id)

    client = get_client(zato_server)

    def _is_gone() -> 'bool':
        try:
            _ = client.invoke(_service_name, {'payload': 'auth-x'})
        except Exception:
            return True
        else:
            return False

    _ = wait_for(_is_gone, f'connection {_conn_name} to be deleted')

# ################################################################################################################################
# ################################################################################################################################
