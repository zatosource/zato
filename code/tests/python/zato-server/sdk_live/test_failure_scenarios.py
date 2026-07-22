# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

# Test suite
from _test_util import create_definition, delete_definition, get_client, read_server_log, wait_for

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

_conn_name = 'My Failure CRM'
_conn_type = 'outconn-crm'

_api_key = 'failure.key.' + CryptoManager.generate_hex_string()
_renewed_api_key = 'renewed.key.' + CryptoManager.generate_hex_string()

_customer_id = 'CUST-7001'

# Longer than the per-call watchdog timeout the stall test uses.
_stall_seconds = 10

# ################################################################################################################################
# ################################################################################################################################

class _TestState:
    """ State shared by the tests, which run in the order they are defined in.
    """
    conn_id = 0

# ################################################################################################################################
# ################################################################################################################################

def test_failure_create_definition(zato_server:'stranydict') -> 'None':
    """ The definition the failure scenarios run against.
    """
    _TestState.conn_id = create_definition(zato_server, _conn_name, _conn_type,
        host='127.0.0.1',
        port=zato_server['echo_port'],
        api_key=_api_key,
    )

# ################################################################################################################################

def test_failure_stall_trips_watchdog(zato_server:'stranydict') -> 'None':
    """ A target that stalls without closing the socket makes the watchdog raise
    in the calling service, and the next call succeeds (7.4, 4.4).
    """
    client = get_client(zato_server)
    echo_state = zato_server['echo_state']

    # The target now answers only after a delay longer than the per-call timeout ..
    echo_state.stall_seconds = _stall_seconds

    try:
        # .. so this call, which carries a two-second timeout, fails through the watchdog ..
        try:
            _ = client.invoke('demo.crm.get-customer-timeout', {'customer_id': _customer_id})
        except Exception:
            watchdog_raised = True
        else:
            watchdog_raised = False

        assert watchdog_raised, 'The watchdog was expected to raise while the target stalls'

    finally:
        # .. and once the target answers normally again, the next call goes through.
        echo_state.stall_seconds = 0

    response = client.invoke('demo.crm.get-customer-timeout', {'customer_id': _customer_id})
    assert response['response'].endswith(f'get-customer {_customer_id}')

# ################################################################################################################################

def test_failure_expired_token_is_refreshed(zato_server:'stranydict') -> 'None':
    """ A target that starts rejecting the auth token makes the framework run
    refresh_credentials and the call succeeds with the fresh token (7.4, 4.5).
    """
    client = get_client(zato_server)
    echo_state = zato_server['echo_state']

    # The target hands this key out to whoever renews ..
    echo_state.renewed_key = _renewed_api_key

    # .. and rejects the key the definition was created with.
    echo_state.expired_keys.add(_api_key)

    try:
        response = client.invoke('demo.crm.get-customer-failure', {'customer_id': _customer_id})
    finally:
        echo_state.expired_keys.discard(_api_key)

    # The reply carries the renewed key, proving the refresh ran and the call was retried.
    assert response['response'] == f'{_renewed_api_key} get-customer {_customer_id}'

    log_content = read_server_log(zato_server)
    assert f'CRM key refreshed for `{_conn_name}`' in log_content

# ################################################################################################################################

def test_failure_target_restart_recovers(zato_server:'stranydict') -> 'None':
    """ Killing and restarting the target leaves the connection usable - validation before use
    notices any dead socket and the framework reconnects on its own (7.4, 4.3).
    """
    port = zato_server['kill_target_server']('echo')
    zato_server['restart_target_server']('echo', port)

    client = get_client(zato_server)

    def _answers() -> 'bool':
        response = client.invoke('demo.crm.get-customer-failure', {'customer_id': _customer_id})
        out = response['response'].endswith(f'get-customer {_customer_id}')
        return out

    _ = wait_for(_answers, 'the connection to recover after the target restart')

# ################################################################################################################################

def test_failure_delete_definition(zato_server:'stranydict') -> 'None':
    """ The failure-scenario definition is removed so later suites start clean.
    """
    delete_definition(zato_server, _TestState.conn_id)

# ################################################################################################################################
# ################################################################################################################################
