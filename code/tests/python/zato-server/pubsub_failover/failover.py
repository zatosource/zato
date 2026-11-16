# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The servers of the active-standby suites, each of which runs in a container of the test runtime image
# with the current tree mounted, on the network of the host, against one shared pub/sub database.

# stdlib
import json
import logging
import os
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass, field
from http.client import OK
from urllib.error import URLError
from urllib.request import Request, urlopen

# Zato
from zato.common.test.conftest_base_pubsub import find_free_port
from zato.common.test.pubsub_database import connect, get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FailoverEnvironment
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import dictlist, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_failover')

# ################################################################################################################################
# ################################################################################################################################

# The image the servers run in and the tree that is mounted into it under its own path.
_runtime_image = 'zato-test-runtime:latest'
_repository_dir = os.environ['ZATO_TEST_BASE_DIR']

# The home directory of the zato user of the image.
_container_home = '/opt/zato'

# The program that a container runs, with the arguments of the start command of a server.
_zato_entrypoint = os.path.join(_repository_dir, 'code', 'bin', 'zato')

# How long a server may take to answer its ping endpoint after its container started, in seconds.
_ready_timeout_seconds = 180

# How often the ping endpoint is checked, in seconds.
_ping_poll_seconds = 0.5

# How long a ping may take, in seconds.
_ping_timeout_seconds = 2

# How long a container may take to stop gracefully, in seconds.
_stop_timeout_seconds = 10

# How long a pulled message waits for its acknowledgement, in seconds, short enough for a test to see
# the messages of lost pull responses handed out again.
_pull_lease_seconds = '5'

# The controller script next to this module.
_controller_path = os.path.join(os.path.dirname(__file__), 'controller.py')

# How often the events of the controller are read while a test waits for a switch, in seconds.
_controller_poll_seconds = 0.5

# How long a link proxy may take to answer its control endpoint after its process started, in seconds.
_proxy_ready_timeout_seconds = 30

# The takeovers that the audit log of a server recorded, with the previous and the new generation of each.
_audit_takeover_query = """
select p.value, g.value
from event e
join event_attr p on p.event_id = e.id and p.name = 'previous_generation'
join event_attr g on g.event_id = e.id and g.name = 'generation'
where e.source = 'pubsub' and e.event_type = 'takeover'
order by e.id
"""

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ContainerServer:
    """ One Zato server of the pair, with the container it runs in.
    """
    name: 'str'
    container_name: 'str'
    server_directory: 'str'
    port: 'int'
    broker_port: 'int'
    env: 'strstrdict' = field(default_factory=dict)

    # A launcher in place of the zato command starts other processes of the container before the server.
    entrypoint: 'str' = _zato_entrypoint

    @property
    def base_url(self) -> 'str':
        out = f'http://127.0.0.1:{self.port}'
        return out

    @property
    def ping_url(self) -> 'str':
        out = f'{self.base_url}/zato/ping'
        return out

# ################################################################################################################################
# ################################################################################################################################

def docker(*args:'str', check:'bool'=True) -> 'subprocess.CompletedProcess[str]':
    out = subprocess.run(['docker', *args], capture_output=True, text=True, check=check)
    return out

# ################################################################################################################################

def _container_command(server:'ContainerServer', action:'str') -> 'strlist':
    """ Builds the docker run or docker create command of a server.
    """
    runtime_dir = get_runtime_dir()

    out:'strlist' = [
        'docker', action,
        '--name', server.container_name,
        '--network', 'host',
        '--user', f'{os.getuid()}:{os.getgid()}',
        '-e', f'HOME={_container_home}',
        '-v', f'{_repository_dir}:{_repository_dir}',
        '-v', f'{runtime_dir}:{runtime_dir}',
    ]

    for name, value in server.env.items():
        out.extend(['-e', f'{name}={value}'])

    # The managed modes resolve their host names through the resolver library, which the server preloads from the same path.
    if preload := os.environ.get('LD_PRELOAD', ''):
        preload_dir = os.path.dirname(preload)
        out.extend(['-e', f'LD_PRELOAD={preload}'])
        out.extend(['-v', f'{preload_dir}:{preload_dir}:ro'])

    out.extend([
        '--entrypoint', server.entrypoint,
        _runtime_image,
        'start', server.server_directory, '--fg',
    ])

    return out

# ################################################################################################################################

def build_server_env(server:'ContainerServer', database:'PubSubDatabase') -> 'None':
    """ Fills in the environment of a server - its ports, the shared pub/sub database
    and the files of its own environment.
    """
    server.env['Zato_Config_Bind_Port'] = str(server.port)
    server.env['Zato_Broker_HTTP_Port'] = str(server.broker_port)
    server.env['Zato_PubSub_Generation_File'] = os.path.join(server.server_directory, 'pubsub-generation')
    server.env['Zato_Audit_Log_DB_Name'] = os.path.join(server.server_directory, 'audit.db')
    server.env['Zato_PubSub_Pull_Lease_Seconds'] = _pull_lease_seconds
    server.env.update(database.env)

# ################################################################################################################################

def run_container(server:'ContainerServer') -> 'None':
    """ Starts a server in a new container.
    """
    _ = docker('rm', '-f', server.container_name, check=False)

    command = _container_command(server, 'run')
    command.insert(2, '-d')

    _ = subprocess.run(command, capture_output=True, text=True, check=True)

# ################################################################################################################################

def create_container(server:'ContainerServer') -> 'None':
    """ Creates the stopped container of a standby server.
    """
    _ = docker('rm', '-f', server.container_name, check=False)
    command = _container_command(server, 'create')
    _ = subprocess.run(command, capture_output=True, text=True, check=True)

# ################################################################################################################################

def remove_container(server:'ContainerServer') -> 'None':
    _ = docker('rm', '-f', server.container_name, check=False)

# ################################################################################################################################

def get_container_state(server:'ContainerServer') -> 'str':
    """ Returns the state of a container - created, running, paused or exited.
    """
    result = docker('inspect', '--format', '{{.State.Status}}', server.container_name)
    out = result.stdout.strip()
    return out

# ################################################################################################################################

def is_server_up(server:'ContainerServer') -> 'bool':
    request = Request(server.ping_url, method='GET')

    try:
        with urlopen(request, timeout=_ping_timeout_seconds) as response:
            out = response.status == OK
    except (OSError, URLError):
        out = False

    return out

# ################################################################################################################################

def wait_until_up(server:'ContainerServer', timeout_seconds:'float'=_ready_timeout_seconds) -> 'float':
    """ Waits until a server answers its ping endpoint and returns how long it took, in seconds.
    """
    start = time.monotonic()
    deadline = start + timeout_seconds

    while not is_server_up(server):
        if time.monotonic() > deadline:
            logs = docker('logs', '--tail', '50', server.container_name, check=False)
            raise Exception(f'Server {server.name} not ready after {timeout_seconds}s:\n{logs.stdout}{logs.stderr}')
        time.sleep(_ping_poll_seconds)

    out = time.monotonic() - start
    logger.info('Server %s ready after %.1fs', server.name, out)

    return out

# ################################################################################################################################

def save_container_logs(server:'ContainerServer', directory:'str') -> 'None':
    """ Copies the output of a container into a file, so that it outlives the container.
    """
    result = docker('logs', server.container_name, check=False)
    path = os.path.join(directory, f'{server.container_name}.log')

    with open(path, 'a') as log_file:
        _ = log_file.write(result.stdout)
        _ = log_file.write(result.stderr)

# ################################################################################################################################
# ################################################################################################################################

def read_generation(database:'PubSubDatabase') -> 'int':
    """ Returns the generation that the active server recorded in the shared database.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('select generation from pubsub_active where id = 1')
        rows = cursor.fetchall()
        out = rows[0][0]
    finally:
        connection.close()

    return out

# ################################################################################################################################

def wait_for_generation(database:'PubSubDatabase', generation:'int', timeout_seconds:'float') -> 'float':
    """ Waits until the shared database records at least the given generation and returns how long it took.
    """
    start = time.monotonic()
    deadline = start + timeout_seconds

    while read_generation(database) < generation:
        if time.monotonic() > deadline:
            raise Exception(f'Generation {generation} not reached after {timeout_seconds}s')
        time.sleep(_ping_poll_seconds)

    out = time.monotonic() - start
    return out

# ################################################################################################################################

def read_audit_rows(server:'ContainerServer', query:'str') -> 'list':
    """ Returns the rows of a query against the audit log of a server, which is a SQLite file in its directory.
    """
    connection = sqlite3.connect(server.env['Zato_Audit_Log_DB_Name'])

    try:
        cursor = connection.cursor()
        _ = cursor.execute(query)
        out = list(cursor.fetchall())
    finally:
        connection.close()

    return out

# ################################################################################################################################

def read_audit_takeovers(server:'ContainerServer', after_generation:'int') -> 'list[tuple[int, int]]':
    """ Returns the previous and the new generation of each takeover that the audit log of a server recorded
    above the given generation, in the order of the takeovers.
    """
    out:'list[tuple[int, int]]' = []

    for previous_value, generation_value in read_audit_rows(server, _audit_takeover_query):
        generation = int(generation_value)
        if generation > after_generation:
            out.append((int(previous_value), generation))

    return out

# ################################################################################################################################

def reset_pair(env:'FailoverEnvironment') -> 'int':
    """ Makes server A the active server and server B a stopped standby, and returns the current generation.
    """
    _ = docker('rm', '-f', env.server_b.container_name, check=False)
    run_container(env.server_a)
    _ = wait_until_up(env.server_a)
    create_container(env.server_b)

    out = read_generation(env.database)
    return out

# ################################################################################################################################
# ################################################################################################################################

class Controller:
    """ The controller script, run as a process of its own for one active and one standby server.
    """

    def __init__(self, active:'ContainerServer', standby:'ContainerServer', events_path:'str') -> 'None':
        self.active = active
        self.standby = standby
        self.events_path = events_path
        self.process:'subprocess.Popen[bytes] | None' = None

    def start(self, interval_seconds:'float'=1.0, max_failures:'int'=3) -> 'None':
        if os.path.exists(self.events_path):
            os.remove(self.events_path)

        command = [
            sys.executable, _controller_path,
            '--active', self.active.container_name,
            '--active-ping-url', self.active.ping_url,
            '--standby', self.standby.container_name,
            '--standby-ping-url', self.standby.ping_url,
            '--interval', str(interval_seconds),
            '--failures', str(max_failures),
            '--events', self.events_path,
        ]

        self.process = subprocess.Popen(command)

    def get_switch_count(self) -> 'int':
        """ Returns how many times the controller has exchanged the roles of the servers so far.
        """
        out = 0

        for event in self.read_events():
            if event['event'] == 'switched':
                out += 1

        return out

    def wait_for_switch(self, timeout_seconds:'float') -> 'None':
        """ Waits until the controller has exchanged the roles of the servers, while it continues to run.
        """
        deadline = time.monotonic() + timeout_seconds

        while self.get_switch_count() == 0:
            assert time.monotonic() < deadline, self.read_events()
            time.sleep(_controller_poll_seconds)

    def stop(self) -> 'None':
        if self.process and self.process.poll() is None:
            self.process.kill()
            _ = self.process.wait()

    def read_events(self) -> 'dictlist':
        out:'dictlist' = []

        with open(self.events_path) as events_file:
            for line in events_file:
                out.append(json.loads(line))

        return out

# ################################################################################################################################
# ################################################################################################################################

class LinkProxy:
    """ A TCP proxy, run as a process of its own, in front of one port of a server - its link to the database
    or its HTTP endpoint - which a test cuts and restores through the control endpoint of the proxy.
    """

    def __init__(self, listen_port:'int', upstream_port:'int', log_path:'str') -> 'None':
        self.listen_port = listen_port
        self.upstream_port = upstream_port
        self.control_port = find_free_port()
        self.log_path = log_path
        self.process:'subprocess.Popen[bytes] | None' = None

    def start(self) -> 'None':
        command = [
            sys.executable, '-m', 'zato.common.test.tcp_proxy',
            '--listen-port', str(self.listen_port),
            '--control-port', str(self.control_port),
            '--upstream-port', str(self.upstream_port),
        ]

        with open(self.log_path, 'wb') as log_file:
            self.process = subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT)

        # The proxy is ready once its control endpoint answers.
        deadline = time.monotonic() + _proxy_ready_timeout_seconds

        while True:
            try:
                _ = self.command('release')
                return
            except OSError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(_ping_poll_seconds)

    def command(self, name:'str') -> 'int':
        """ Sends one command to the control endpoint of the proxy and returns its numeric result.
        """
        url = f'http://127.0.0.1:{self.control_port}/{name}'

        with urlopen(url, timeout=_ping_timeout_seconds) as response:
            out = int(response.read())

        return out

    def stop(self) -> 'None':
        if self.process and self.process.poll() is None:
            self.process.kill()
            _ = self.process.wait()

# ################################################################################################################################
# ################################################################################################################################

def get_failover_dir() -> 'str':
    """ Returns the directory of the runtime data of the active-standby suites.
    """
    out = os.path.join(get_runtime_dir(), 'failover')
    os.makedirs(out, exist_ok=True)

    return out

# ################################################################################################################################
# ################################################################################################################################
