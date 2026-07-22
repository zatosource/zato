# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import sys

# Test suite
from _test_util import create_definition, delete_definition, get_client, wait_for

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

_fixtures_directory = os.path.join(os.path.dirname(__file__), 'fixtures')

_jar_path = os.path.join(_fixtures_directory, 'echo-server.jar')
_module_path = os.path.join(_fixtures_directory, 'textproc_module.py')
_tunnelctl_path = os.path.join(_fixtures_directory, 'tunnelctl')

# ################################################################################################################################
# ################################################################################################################################

class _TestState:
    """ State shared by the tests, which run in the order they are defined in.
    """
    inventory_conn_id = 0
    textproc_conn_id = 0
    tunnel_conn_id = 0
    tunnel_pid = 0

# ################################################################################################################################
# ################################################################################################################################

def _is_pid_running(pid:'int') -> 'bool':
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    else:
        return True

# ################################################################################################################################
# ################################################################################################################################

def test_jar_create_definition(zato_server:'stranydict') -> 'None':
    """ A definition wrapping the Java component can be created - starting it runs the jar
    as a supervised helper process (3.1).
    """
    _TestState.inventory_conn_id = create_definition(zato_server, 'My Inventory', 'outconn-inventory',
        jar_path=_jar_path,
    )

# ################################################################################################################################

def test_jar_invoke(zato_server:'stranydict') -> 'None':
    """ A service round trip through the Java helper process.
    """
    client = get_client(zato_server)

    response = client.invoke('demo.inventory.get-stock', {'item': 'widget'})
    text = response['response']

    # The reply carries the helper's own pid, proving the call went through the jar.
    marker, pid, echoed = text.split(' ', 2)
    assert marker == 'jar'
    assert int(pid)
    assert echoed == 'stock widget'

# ################################################################################################################################

def test_jar_kill_restarts_helper(zato_server:'stranydict') -> 'None':
    """ Killing the helper process makes the framework rebuild the connection, re-running
    create_client, which starts a new helper (7.10).
    """
    client = get_client(zato_server)

    # The pid of the helper as it runs now.
    response = client.invoke('demo.inventory.get-stock', {'item': 'widget'})
    old_pid = int(response['response'].split(' ', 2)[1])

    # Kill it the hard way, as a crash would.
    os.kill(old_pid, signal.SIGKILL)

    # The framework noticed, rebuilt the connection and a new helper answers with a new pid.
    def _new_helper_answers() -> 'bool':
        reply = client.invoke('demo.inventory.get-stock', {'item': 'widget'})
        new_pid = int(reply['response'].split(' ', 2)[1])
        out = new_pid != old_pid
        return out

    _ = wait_for(_new_helper_answers, 'a new helper process to answer after the kill')

# ################################################################################################################################

def test_jar_delete_stops_helper(zato_server:'stranydict') -> 'None':
    """ Deleting the definition stops the helper process.
    """
    client = get_client(zato_server)

    response = client.invoke('demo.inventory.get-stock', {'item': 'widget'})
    helper_pid = int(response['response'].split(' ', 2)[1])

    delete_definition(zato_server, _TestState.inventory_conn_id)

    def _helper_gone() -> 'bool':
        out = not _is_pid_running(helper_pid)
        return out

    _ = wait_for(_helper_gone, 'the helper process to stop with the definition')

# ################################################################################################################################
# ################################################################################################################################

def test_runner_create_definition(zato_server:'stranydict') -> 'None':
    """ A definition wrapping a library run in a clean interpreter can be created - starting it runs
    the stock runner in a clean interpreter (3.2).
    """
    _TestState.textproc_conn_id = create_definition(zato_server, 'My TextProc', 'outconn-textproc',
        python_path=sys.executable,
        module_path=_module_path,
    )

# ################################################################################################################################

def test_runner_invoke(zato_server:'stranydict') -> 'None':
    """ A service round trip through the module in its clean interpreter.
    """
    client = get_client(zato_server)

    response = client.invoke('demo.textproc.transform', {'text': 'hello'})
    text = response['response']

    # The reply carries the runner's own pid, proving the call ran in another interpreter.
    assert text.startswith('HELLO pid=')
    runner_pid = int(text.split('pid=')[1])
    assert runner_pid

# ################################################################################################################################

def test_runner_kill_restarts_helper(zato_server:'stranydict') -> 'None':
    """ Killing the runner process makes the framework rebuild the connection,
    starting a new runner (7.11).
    """
    client = get_client(zato_server)

    response = client.invoke('demo.textproc.transform', {'text': 'hello'})
    old_pid = int(response['response'].split('pid=')[1])

    os.kill(old_pid, signal.SIGKILL)

    def _new_runner_answers() -> 'bool':
        reply = client.invoke('demo.textproc.transform', {'text': 'hello'})
        new_pid = int(reply['response'].split('pid=')[1])
        out = new_pid != old_pid
        return out

    _ = wait_for(_new_runner_answers, 'a new runner process to answer after the kill')

# ################################################################################################################################

def test_runner_delete_definition(zato_server:'stranydict') -> 'None':
    """ Deleting the definition stops the runner process.
    """
    client = get_client(zato_server)

    response = client.invoke('demo.textproc.transform', {'text': 'hello'})
    runner_pid = int(response['response'].split('pid=')[1])

    delete_definition(zato_server, _TestState.textproc_conn_id)

    def _runner_gone() -> 'bool':
        out = not _is_pid_running(runner_pid)
        return out

    _ = wait_for(_runner_gone, 'the runner process to stop with the definition')

# ################################################################################################################################
# ################################################################################################################################

def test_cli_create_definition(zato_server:'stranydict') -> 'None':
    """ A definition wrapping a CLI tool can be created - starting it runs the tool's
    long-lived session as a supervised helper process (3.3).
    """
    _TestState.tunnel_conn_id = create_definition(zato_server, 'My Tunnel', 'outconn-tunnel',
        binary_path=_tunnelctl_path,
    )

# ################################################################################################################################

def test_cli_long_lived_session(zato_server:'stranydict') -> 'None':
    """ The long-lived session serves the tunnel's address the way ngrok serves its API.
    """
    client = get_client(zato_server)

    response = client.invoke('demo.tunnel.get-address', {})
    text = response['response']

    assert text.startswith('tcp://127.0.0.1:20000 pid=')
    _TestState.tunnel_pid = int(text.split('pid=')[1])

# ################################################################################################################################

def test_cli_one_shot_command(zato_server:'stranydict') -> 'None':
    """ A one-shot command runs the binary and returns its output as a method result.
    """
    client = get_client(zato_server)

    response = client.invoke('demo.tunnel.get-status', {'name': 'alpha'})
    assert response['response'] == '{"name": "alpha", "status": "active"}'

# ################################################################################################################################

def test_cli_delete_stops_tunnel(zato_server:'stranydict') -> 'None':
    """ Deleting the definition stops the tunnel - the long-lived session dies with it (3.3).
    """
    delete_definition(zato_server, _TestState.tunnel_conn_id)

    def _tunnel_gone() -> 'bool':
        out = not _is_pid_running(_TestState.tunnel_pid)
        return out

    _ = wait_for(_tunnel_gone, 'the tunnel process to stop with the definition')

# ################################################################################################################################
# ################################################################################################################################
