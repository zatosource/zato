# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import subprocess
import tempfile
import threading
import time

# PyYAML
import yaml

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import AdminClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.sdk_live.pooled')

# ################################################################################################################################
# ################################################################################################################################

_conn_name = 'My Mainframe'
_conn_type = 'outconn-mainframe'
_service_name = 'demo.mainframe.send-command'

_logon_token = 'logon.token.' + CryptoManager.generate_hex_string()
_logon_token_enmasse = 'logon.token.' + CryptoManager.generate_hex_string()

_pool_size = 3

_wait_timeout = 60
_poll_interval = 0.5
_enmasse_timeout = 180

_zato_bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# ################################################################################################################################
# ################################################################################################################################

class _TestState:
    """ State shared by the tests, which run in the order they are defined in.
    """
    conn_id = 0

# ################################################################################################################################
# ################################################################################################################################

def _get_client(zato_server:'stranydict') -> 'AdminClient':
    out = AdminClient(zato_server['base_url'], zato_server['invoke_password'])
    return out

# ################################################################################################################################

def _read_server_log(zato_server:'stranydict') -> 'str':
    log_path = os.path.join(zato_server['server_directory'], 'logs', 'server.log')

    with open(log_path, 'r') as log_file:
        out = log_file.read()

    return out

# ################################################################################################################################

def _wait_for(condition:'callable_', description:'str', timeout:'int'=_wait_timeout) -> 'any_':
    """ Polls the condition until it returns a truthy value or the timeout passes.
    """
    deadline = time.monotonic() + timeout
    last_error = ''

    while time.monotonic() < deadline:

        try:
            result = condition()
        except Exception as e:
            last_error = str(e)
        else:
            if result:
                return result

        time.sleep(_poll_interval)

    raise Exception(f'Timed out waiting for {description} after {timeout}s, last error: {last_error}')

# ################################################################################################################################

def _run_enmasse(arguments:'list', zato_server:'stranydict') -> 'None':
    """ Runs the enmasse command against the suite's server, raising an exception if it fails.
    """
    command = [_zato_bin, 'enmasse', zato_server['server_directory']] + arguments + ['--verbose']

    result = subprocess.run(command, capture_output=True, text=True, timeout=_enmasse_timeout)
    if result.returncode != 0:
        raise Exception(f'enmasse failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################
# ################################################################################################################################

def test_pooled_type_registered(zato_server:'stranydict') -> 'None':
    """ The connector module deployed at boot registered its connection type.
    """
    def _is_registered() -> 'bool':
        log_content = _read_server_log(zato_server)
        out = f'Registered connector type `{_conn_type}`' in log_content
        return out

    _ = _wait_for(_is_registered, f'connector type {_conn_type} to register')

# ################################################################################################################################

def test_pooled_create_definition(zato_server:'stranydict') -> 'None':
    """ A definition of the pooled type can be created and pinged - the ping itself
    borrows a connection from the pool, which logs on to the gateway.
    """
    client = _get_client(zato_server)

    response = client.create('zato.generic.connection.create',
        cluster_id=1,
        name=_conn_name,
        type_=_conn_type,
        is_active=True,
        is_internal=False,
        is_channel=False,
        is_outconn=True,
        host='127.0.0.1',
        port=zato_server['handshake_port'],
        logon_token=_logon_token,
        pool_size=_pool_size,
    )

    _TestState.conn_id = response['id']
    assert _TestState.conn_id

    # The connection builds in the background, so keep pinging until it answers.
    def _ping() -> 'bool':
        ping_response = client.invoke('zato.generic.connection.ping', {'id': _TestState.conn_id})
        out = ping_response['is_success'] is True
        return out

    _ = _wait_for(_ping, f'connection {_conn_name} to answer pings')

# ################################################################################################################################

def test_pooled_invoke_runs_hooks(zato_server:'stranydict') -> 'None':
    """ A service invocation borrows a pooled connection, gets the gateway's reply
    and both pool hooks run around the call.
    """
    client = _get_client(zato_server)

    response = client.invoke(_service_name, {'command': 'hello'})

    # The gateway prepends the session ID it assigned during the logon handshake.
    text = response['response']
    session_id, command = text.split(' ', 1)

    assert session_id.startswith('session-')
    assert command == 'hello'

    # Both pool hooks logged their runs.
    log_content = _read_server_log(zato_server)
    assert f'Mainframe session `{session_id}` taken from pool' in log_content
    assert f'Mainframe session `{session_id}` returned to pool' in log_content

# ################################################################################################################################

def test_pooled_concurrent_invocations_use_distinct_connections(zato_server:'stranydict') -> 'None':
    """ Concurrent service invocations borrow distinct pooled connections - each reply carries
    the session ID of the connection that served it, so distinct IDs prove distinct connections.
    """
    session_ids = []
    errors = []
    lock = threading.Lock()

    def _invoke_slow_command(index:'int') -> 'None':
        try:
            # Each thread needs its own client
            client = _get_client(zato_server)

            # A slow command keeps its connection busy long enough for all the calls to overlap
            response = client.invoke(_service_name, {'command': f'slow check-{index}'})
            session_id = response['response'].split(' ', 1)[0]

            with lock:
                session_ids.append(session_id)

        except Exception as e:
            with lock:
                errors.append(str(e))

    threads = [threading.Thread(target=_invoke_slow_command, args=(index,)) for index in range(_pool_size)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(_wait_timeout)

    assert not errors, f'Concurrent invocations failed: {errors}'
    assert len(session_ids) == _pool_size

    # Each concurrent call was served by a different pooled connection
    assert len(set(session_ids)) == _pool_size, f'Expected {_pool_size} distinct sessions, got {session_ids}'

# ################################################################################################################################

def test_pooled_delete_definition(zato_server:'stranydict') -> 'None':
    """ Deleting the definition stops the pool, closing each pooled connection through on_stop.
    """
    client = _get_client(zato_server)

    _ = client.delete('zato.generic.connection.delete', id=_TestState.conn_id)

    # The definition disappears from the container, so invoking the service starts to fail ..
    def _is_gone() -> 'bool':
        try:
            _ = client.invoke(_service_name, {'command': 'hello'})
        except Exception:
            return True
        else:
            return False

    _ = _wait_for(_is_gone, f'connection {_conn_name} to be deleted')

    # .. and every pooled connection was closed through the connector's on_stop hook.
    def _all_closed() -> 'bool':
        log_content = _read_server_log(zato_server)
        out = f'closed for `{_conn_name}`' in log_content
        return out

    _ = _wait_for(_all_closed, 'the pooled connections to be closed')

# ################################################################################################################################

def test_pooled_enmasse_import_starts_connection(zato_server:'stranydict') -> 'None':
    """ Importing a custom_mainframe definition with enmasse creates the pooled connection
    on the live server and services can use it right away, with no restarts.
    """
    yaml_content = f"""
custom_mainframe:
  - name: {_conn_name}
    host: 127.0.0.1
    port: {zato_server['handshake_port']}
    logon_token: {_logon_token_enmasse}
"""

    import_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml', mode='w')
    _ = import_file.write(yaml_content)
    import_file.close()

    try:
        # The import writes the definition to the database and reloads the server's configuration.
        _run_enmasse(['--import', '--input', import_file.name], zato_server)
    finally:
        os.unlink(import_file.name)

    # The service borrows a connection from the pool the import created.
    client = _get_client(zato_server)

    def _answers() -> 'bool':
        response = client.invoke(_service_name, {'command': 'hello'})
        out = response['response'].endswith(' hello')
        return out

    _ = _wait_for(_answers, 'the enmasse-imported pooled connection to answer')

# ################################################################################################################################

def test_pooled_enmasse_export_round_trip(zato_server:'stranydict') -> 'None':
    """ Exporting with enmasse returns the definition under its custom_mainframe key with the fields intact.
    """
    export_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
    export_file.close()

    try:
        _run_enmasse(['--export', '--output', export_file.name, '--include-type', 'custom_mainframe'], zato_server)

        with open(export_file.name, 'r') as f:
            exported = yaml.safe_load(f.read())
    finally:
        os.unlink(export_file.name)

    # The definition is under its own top-level key ..
    items = exported['custom_mainframe']
    assert len(items) == 1

    # .. and the fields the YAML carried on import survived the round trip.
    item = items[0]
    assert item['name'] == _conn_name
    assert item['host'] == '127.0.0.1'
    assert item['port'] == zato_server['handshake_port']
    assert item['logon_token'] == _logon_token_enmasse

# ################################################################################################################################
# ################################################################################################################################
