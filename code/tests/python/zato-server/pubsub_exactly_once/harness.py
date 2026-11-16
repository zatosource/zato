# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import signal
import subprocess
import time
from base64 import b64encode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.test.config_pubsub_exactly_once import TestConfig
from zato.common.test.conftest_base_pubsub import find_free_port, render_template, start_server_process, wait_for_server
from zato.common.test.exactly_once import assert_exactly_once, hold, Input_Topic, release, wait_for_outputs, wait_until_held
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from sqlalchemy.engine import Engine
    from zato.common.test.exactly_once import OutputCheck
    from zato.common.typing_ import any_, anydict, intlist, strlist

    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# The process name of the worker of a server
_worker_process_name = 'zato-worker'

# How long the tests wait for a held key, an imported definition, a new worker and the outputs, in seconds
Hold_Timeout     = 30.0
Enmasse_Timeout  = 120
Worker_Timeout   = 120.0
Settle_Timeout   = 120.0

# How long a stopped server is given to exit, in seconds
_stop_timeout = 120

# How often the processes of the server are looked at, in seconds
_poll_seconds = 0.2

# The time between the request to stop the server and the release of the held key, in seconds
_stop_release_delay = 1.0

# The status code of a request that succeeded
Status_OK = 200

# ################################################################################################################################
# ################################################################################################################################

def new_keys(count:'int') -> 'tuple[str, strlist]':
    """ Returns a prefix unique to one test and that many keys under it, in the order of their publication.
    """
    suffix = CryptoManager.generate_hex_string(8)
    prefix = f'exactly-once.{suffix}.'

    keys:'strlist' = []

    for index in range(count):
        keys.append(f'{prefix}{index:06d}')

    out = (prefix, keys)
    return out

# ################################################################################################################################

def post_json(path:'str', username:'str', password:'str', payload:'any_') -> 'tuple[int, anydict]':
    """ Sends one request with basic authentication and returns its status code and its parsed body.
    """
    url = f'{TestConfig.base_url}{path}'

    serialized = json.dumps(payload)
    body = serialized.encode()

    credentials = f'{username}:{password}'
    encoded = b64encode(credentials.encode())

    request = Request(url, data=body, method='POST')
    request.add_header('Authorization', f'Basic {encoded.decode()}')
    request.add_header('Content-Type', 'application/json')

    try:
        with urlopen(request) as response:
            raw = response.read()
            status_code = response.status
    except HTTPError as error:
        raw = error.read()
        status_code = error.code

    if raw:
        response_body = json.loads(raw)
    else:
        response_body = {}

    out = (status_code, response_body)
    return out

# ################################################################################################################################

def publish_input(key:'str') -> 'None':
    """ Publishes one input message of the relay over REST.
    """
    status_code, body = post_json(f'/pubsub/topic/{Input_Topic}',
        TestConfig.publisher_username, TestConfig.publisher_password, {'data': {'key': key}})

    assert status_code == Status_OK, (status_code, body)

# ################################################################################################################################

def publish_inputs(keys:'strlist') -> 'None':
    """ Publishes the input messages of the relay in the order of the keys.
    """
    for key in keys:
        publish_input(key)

# ################################################################################################################################

def get_engine() -> 'Engine':
    """ Returns the engine of the pub/sub database of the server.
    """
    out = get_pubsub_engine()
    return out

# ################################################################################################################################

def verify(prefix:'str', keys:'strlist') -> 'OutputCheck':
    """ Waits until the delivery of the keys settles and asserts that each of them was relayed exactly once and in order.
    """
    engine = get_engine()
    out = wait_for_outputs(engine, keys, prefix, Settle_Timeout)

    assert_exactly_once(out, keys)
    return out

# ################################################################################################################################

def stage_batch(keys:'strlist') -> 'None':
    """ Makes all the keys but the first one go out in one batch whose last key is held, with all the others processed.
    The first key is held until the others are published, so that the next batch reads all of them at once.
    """
    gate_key = keys[0]
    last_key = keys[-1]

    hold(gate_key)
    hold(last_key)

    publish_input(gate_key)
    wait_until_held(gate_key, Hold_Timeout)

    publish_inputs(keys[1:])
    release(gate_key)

    wait_until_held(last_key, Hold_Timeout)

# ################################################################################################################################
# ################################################################################################################################

def import_enmasse(is_relay_active:'bool') -> 'None':
    """ Imports the definitions of the suite into the running server, with the delivery of the relay active or paused.
    """
    placeholders = dict(TestConfig.placeholders)

    if is_relay_active:
        placeholders['relay_delivery_active'] = 'true'
    else:
        placeholders['relay_delivery_active'] = 'false'

    rendered = render_template(TestConfig.template_path, placeholders)

    control_dir = cast_('str', TestConfig.session_state.test_data_directory)
    rendered_path = os.path.join(control_dir, 'enmasse.yaml')

    with open(rendered_path, 'w') as rendered_file:
        _ = rendered_file.write(rendered)

    environment = os.environ.copy()
    _ = environment.pop('COVERAGE_PROCESS_START', None)

    command = [TestConfig.zato_bin, 'enmasse', TestConfig.server_directory, '--verbose',
        '--import', '--input', rendered_path, '--missing-wait-time', '15']

    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=Enmasse_Timeout, env=environment)

    assert result.returncode == 0, f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'

# ################################################################################################################################
# ################################################################################################################################

def _get_server_process() -> 'Popen[bytes]':
    """ Returns the process that started the server of the session, which a running server always has.
    """
    out = cast_('Popen[bytes]', TestConfig.session_state.server_process)
    return out

# ################################################################################################################################

def _get_parent_pids() -> 'dict[int, int]':
    """ Returns the parent of each process of the system, by process ID.
    """
    out:'dict[int, int]' = {}

    for name in os.listdir('/proc'):

        if not name.isdigit():
            continue

        try:
            with open(f'/proc/{name}/stat') as stat_file:
                stat = stat_file.read()
        except FileNotFoundError:
            continue

        # The process name is in parentheses and may contain spaces, the parent follows the state after it
        _, _, rest = stat.rpartition(')')
        fields = rest.split()

        out[int(name)] = int(fields[1])

    return out

# ################################################################################################################################

def _get_server_pids() -> 'intlist':
    """ Returns the processes of the server of the session, which descend from the process that started it.
    """
    server_process = _get_server_process()
    root_pid = server_process.pid
    parents = _get_parent_pids()

    out:'intlist' = [root_pid]

    for pid in parents:
        ancestor = parents[pid]

        while ancestor in parents:
            if ancestor == root_pid:
                out.append(pid)
                break
            ancestor = parents[ancestor]

    return out

# ################################################################################################################################

def find_worker_pid() -> 'int':
    """ Returns the process ID of the worker of the server.
    """
    for pid in _get_server_pids():

        try:
            with open(f'/proc/{pid}/comm') as comm_file:
                comm = comm_file.read()
        except FileNotFoundError:
            continue

        if comm.strip() == _worker_process_name:
            return pid

    raise Exception('No worker process of the server found')

# ################################################################################################################################

def kill_worker() -> 'None':
    """ Kills the worker of the server with SIGKILL and waits until the arbiter has started a new one that responds.
    """
    old_pid = find_worker_pid()
    os.kill(old_pid, signal.SIGKILL)

    deadline = time.monotonic() + Worker_Timeout

    while True:

        if time.monotonic() > deadline:
            raise Exception(f'No new worker within {Worker_Timeout}s')

        try:
            new_pid = find_worker_pid()
        except Exception:
            new_pid = old_pid

        if new_pid != old_pid:
            break

        time.sleep(_poll_seconds)

    wait_for_server(TestConfig.logger, '127.0.0.1', TestConfig.server_port)

# ################################################################################################################################

def start_server() -> 'None':
    """ Starts the server of the session again and waits until its worker is ready.
    """
    broker_port = find_free_port()

    _ = start_server_process(
        state=TestConfig.session_state,
        logger=TestConfig.logger,
        zato_bin=TestConfig.zato_bin,
        server_directory=TestConfig.server_directory,
        server_port=TestConfig.server_port,
        broker_port=broker_port,
        extra_server_env=TestConfig.extra_server_env,
        patch_server_conf_bind=True,
    )

# ################################################################################################################################

def stop_server_releasing(key:'str') -> 'None':
    """ Stops the server with `zato stop`, releases the held key while the server drains its deliveries,
    and waits until the server has exited.
    """
    command = [TestConfig.zato_bin, 'stop', TestConfig.server_directory]
    stop_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(_stop_release_delay)
    release(key)

    _ = stop_process.wait(timeout=_stop_timeout)

    server_process = _get_server_process()
    _ = server_process.wait(timeout=_stop_timeout)

# ################################################################################################################################

def kill_server() -> 'None':
    """ Kills the arbiter and the worker of the server with SIGKILL.
    """
    server_process = _get_server_process()

    for pid in _get_server_pids():
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    _ = server_process.wait(timeout=_stop_timeout)

# ################################################################################################################################
# ################################################################################################################################
