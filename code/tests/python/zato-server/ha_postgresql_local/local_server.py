# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A server started by the command that an active-standby node runs, `zato start <dir> --fg`, with the generation
# of a node, on the Zato database of the session and on reserved ports. The output of the server is streamed into
# the log of the test, together with the moments at which the server reports each stage of its start.

# stdlib
import logging
import os
import re
import shlex
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from http.client import OK
from urllib.error import URLError
from urllib.request import Request, urlopen

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import SessionState, get_server_environment, patch_server_conf, \
     run_quickstart_and_enmasse
from zato.common.test.process_util import get_process_tree_pids
from zato.common.test.pubsub_database import connect
from zato.common.test.reservation import PortInUse, reserve_port, start_on_reserved_port
from zato.common.test.takeover import ModuleCtx as TakeoverCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.test.reservation import PortReservation
    from zato.common.typing_ import any_, intlist, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

stage_list = list['Stage']

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variable through which an active-standby node passes its generation to its server
    Env_HA_Generation = 'Zato_HA_Generation'

    # The variable with the FIFO through which an active-standby node activates its warm server
    Env_HA_Activation_Path = 'Zato_HA_Activation_Path'

    # The purpose under which the ports of the server are reserved
    Port_Purpose = 'ha-postgresql-local-server'

    # How long the test waits for the first answer before it gives up
    Start_Timeout = 120.0

    # How long after the first answer the stages that the server reports later may take
    Stage_Timeout = 30.0

    # How often the readiness of the server is checked, and how long each check may take
    Ping_Interval = 0.02
    Ping_Timeout = 0.25

    # How far above the stored generation the node of the test begins
    Generation_Step = 100

    # The prefix of the quickstart directory and the name of the logger of the session
    Quickstart_Prefix = 'zato_ha_local_server_'
    Logger_Name = 'zato.test.ha_postgresql_local'

    # How long the stream of the output may take to finish once the server has been killed
    Stream_Join_Timeout = 10.0

    # The variable with the command of a recorder that the server is started through, e.g. perf of bin/perf-run,
    # and how long the recorder may take to write its output once the server has exited
    Env_Command_Prefix = 'Zato_Test_Server_Command_Prefix'
    Recorder_Exit_Timeout = 60.0

    # The entry of the output of a server whose listening socket could not bind its port
    Port_In_Use_Pattern = re.compile(r'Address already in use')

    # The file of the name of a process
    Proc_Comm_Path = '/proc/{}/comm'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Stage:
    """ A stage of the start, the entry of the log that reports it, and when that entry was read, counted from the spawn.
    """
    name: 'str'
    pattern: 're.Pattern[str]'
    elapsed: 'float | None'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LocalServer:
    """ A server of the session, its directory, its ports and, once spawned, its process and the stream of its output.
    """
    state: 'SessionState'
    database: 'PubSubDatabase'
    zato_bin: 'str'
    server_dir: 'str'
    invoke_password: 'str'

    broker_port: 'PortReservation'
    mllp_port: 'PortReservation'
    server_port: 'PortReservation | None'

    base_url: 'str'
    ping_url: 'str'

    process: 'subprocess.Popen[bytes] | None'
    stream_thread: 'threading.Thread | None'
    output: 'strlist'
    stages: 'stage_list'

    spawned_at: 'float'
    spawned_at_epoch: 'float'

# ################################################################################################################################
# ################################################################################################################################

def _new_stage(name:'str', pattern:'str') -> 'Stage':
    """ Returns a stage that has not been reached yet.
    """
    out = Stage()
    out.name = name
    out.pattern = re.compile(pattern)
    out.elapsed = None

    return out

# ################################################################################################################################

def new_stages() -> 'stage_list':
    """ Returns the stages of the start in the order in which the server reaches them, each named after what precedes
    the entry that ends it - the interpreter and the CLI before the arbiter reads its configuration, the reading
    of the configuration, the schemas and the raise of the generation, the fork of the config process, the config
    process until it is ready, the fork of the worker and the worker until it is ready.
    """
    out = [
        _new_stage('cli_and_interpreter', r' - Getting configuration from `[^`]*/server\.conf`'),
        _new_stage('configuration', r' - Getting configuration from `[^`]*/sql\.conf`'),
        _new_stage('schemas_and_raise', r' - Pub/sub generation raised -> \d+, owner:'),
        _new_stage('config_process_fork', r' - Started config process, generation \d+, PID \d+'),
        _new_stage('config_process', r' - Config process, generation \d+, PID \d+ is ready'),
        _new_stage('worker_fork', r' - Started worker, generation \d+, PID \d+'),
        _new_stage('worker', r' - Worker, generation \d+, PID \d+ is ready'),
    ]

    return out

# ################################################################################################################################
# ################################################################################################################################

def read_generation(database:'PubSubDatabase') -> 'int':
    """ Returns the generation of the active server as the database holds it.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('select generation from zato_active where id = 1')
        row:'any_' = cursor.fetchone()
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def next_generation(database:'PubSubDatabase') -> 'int':
    """ Returns a generation of a node above the one that the database holds.
    """
    stored_generation = read_generation(database)

    out = stored_generation + ModuleCtx.Generation_Step
    return out

# ################################################################################################################################

def _stream_output(server:'LocalServer', process:'subprocess.Popen[bytes]') -> 'None':
    """ Logs each line of the output of the server, keeps it, and records when each stage was first reported.
    """
    stdout:'any_' = process.stdout

    for line in iter(stdout.readline, b''):
        text = line.decode('utf-8', errors='replace').rstrip()
        elapsed = time.monotonic() - server.spawned_at

        logger.debug('[SERVER %6.3fs] %s', elapsed, text)
        server.output.append(text)

        for stage in server.stages:
            if stage.elapsed is None:
                if stage.pattern.search(text):
                    stage.elapsed = elapsed

# ################################################################################################################################

def get_command_prefix() -> 'strlist':
    """ Returns the command of the recorder that the server is started through, or an empty list without one.
    """
    prefix = os.environ.get(ModuleCtx.Env_Command_Prefix, '')

    out = shlex.split(prefix)
    return out

# ################################################################################################################################

def is_answering(ping_url:'str', timeout:'float') -> 'bool':
    """ Whether /zato/ping of the server answers with 200 within the timeout.
    """
    request = Request(ping_url, method='GET')

    try:
        with urlopen(request, timeout=timeout) as response:
            out = response.status == OK
    except (OSError, URLError):
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

def create_local_server(database:'PubSubDatabase', rendered_yaml:'str'='') -> 'LocalServer':
    """ Creates the environment of a server on the database of the session, with the objects of the enmasse YAML, if any,
    and reserves its broker and MLLP ports. The port of the server is reserved when the server is started.
    """
    state = SessionState(ModuleCtx.Logger_Name, '')
    zato_bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')
    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

    work_dir_env:'strstrdict' = dict(database.env)

    server_dir = run_quickstart_and_enmasse(
        state=state,
        logger=logger,
        zato_bin=zato_bin,
        invoke_password=invoke_password,
        rendered_yaml=rendered_yaml,
        quickstart_prefix=ModuleCtx.Quickstart_Prefix,
        extra_env=work_dir_env,
        log_to_files=False,
    )

    out = LocalServer()
    out.state = state
    out.database = database
    out.zato_bin = zato_bin
    out.server_dir = server_dir
    out.invoke_password = invoke_password

    out.broker_port = reserve_port(ModuleCtx.Port_Purpose)
    out.mllp_port = reserve_port(ModuleCtx.Port_Purpose)
    out.server_port = None

    out.base_url = ''
    out.ping_url = ''

    out.process = None
    out.stream_thread = None
    out.output = []
    out.stages = new_stages()

    out.spawned_at = 0.0
    out.spawned_at_epoch = 0.0

    return out

# ################################################################################################################################

def bind_local_server(server:'LocalServer', port:'int') -> 'None':
    """ Sets the port of the server in its configuration.
    """
    patch_server_conf(server.server_dir, port, True)

# ################################################################################################################################

def _new_server_env(server:'LocalServer') -> 'strstrdict':
    """ Returns the variables of the Zato database and of the generation file that every start of the server is given.
    """
    out:'strstrdict' = dict(server.database.env)
    out[TakeoverCtx.Env_Generation_File] = os.path.join(server.server_dir, TakeoverCtx.Generation_File_Name)

    return out

# ################################################################################################################################

def spawn_local_server(server:'LocalServer', port:'int') -> 'None':
    """ Spawns the server on the port of its configuration with the generation of a node above the one that the database
    holds, by the command of the node, through the command of a recorder if one is given.
    """
    generation = next_generation(server.database)

    server_env = _new_server_env(server)
    server_env[ModuleCtx.Env_HA_Generation] = f'{generation}'

    _spawn(server, port, server_env)

# ################################################################################################################################

def spawn_warm_local_server(server:'LocalServer', port:'int', activation_path:'str') -> 'None':
    """ Spawns the server on the port of its configuration without a generation, as a node spawns its warm server,
    so that the server waits until a generation is written to the activation path.
    """
    server_env = _new_server_env(server)
    server_env[ModuleCtx.Env_HA_Activation_Path] = activation_path

    _spawn(server, port, server_env)

# ################################################################################################################################

def _spawn(server:'LocalServer', port:'int', server_env:'strstrdict') -> 'None':
    """ Spawns the server on the port of its configuration with the variables given, by the command of the node,
    through the command of a recorder if one is given.
    """
    env = get_server_environment(port, server.broker_port.port, server.mllp_port.port, server_env)

    command_prefix = get_command_prefix()
    command = [*command_prefix, server.zato_bin, 'start', server.server_dir, '--fg']

    server.base_url = f'http://127.0.0.1:{port}'
    server.ping_url = f'{server.base_url}/zato/ping'
    server.output = []
    server.stages = new_stages()

    server.spawned_at = time.monotonic()
    server.spawned_at_epoch = time.time()

    # The server runs in a process group of its own, as it does under a node.
    process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, process_group=0)

    server.process = process
    server.state.server_process = process

    stream_thread = threading.Thread(target=_stream_output, args=(server, process), daemon=True)
    stream_thread.start()

    server.stream_thread = stream_thread

# ################################################################################################################################

def wait_for_answer(server:'LocalServer') -> 'float':
    """ Returns how long after the spawn /zato/ping first answered with 200. A server that exits because its port
    is in use raises PortInUse, so that the start is repeated on another port.
    """
    process:'any_' = server.process
    deadline = server.spawned_at + ModuleCtx.Start_Timeout

    while time.monotonic() < deadline:

        if is_answering(server.ping_url, ModuleCtx.Ping_Timeout):
            out = time.monotonic() - server.spawned_at
            return out

        if process.poll() is not None:

            stream_thread:'any_' = server.stream_thread
            stream_thread.join(ModuleCtx.Stream_Join_Timeout)

            for line in server.output:
                if ModuleCtx.Port_In_Use_Pattern.search(line):
                    raise PortInUse(line)

            raise Exception(f'Server exited with {process.returncode} before it answered')

        time.sleep(ModuleCtx.Ping_Interval)

    raise Exception(f'Server did not answer within {ModuleCtx.Start_Timeout}s')

# ################################################################################################################################

def start_local_server(server:'LocalServer') -> 'float':
    """ Starts the server on a reserved port, repeating the start on another port if its own was taken,
    and returns how long after the spawn the server first answered.
    """
    def start(port:'int') -> 'float':
        bind_local_server(server, port)
        spawn_local_server(server, port)

        out = wait_for_answer(server)
        return out

    started = start_on_reserved_port(ModuleCtx.Port_Purpose, start)
    server.server_port = started.reservation

    out = started.result
    return out

# ################################################################################################################################

def wait_for_stages(server:'LocalServer') -> 'None':
    """ Waits until every stage was reported, including those that the server reports after its first answer.
    """
    deadline = time.monotonic() + ModuleCtx.Stage_Timeout

    for stage in server.stages:
        while stage.elapsed is None:
            if time.monotonic() > deadline:
                raise Exception(f'Stage {stage.name} not reported within {ModuleCtx.Stage_Timeout}s')
            time.sleep(ModuleCtx.Ping_Interval)

# ################################################################################################################################

def get_server_pids(server:'LocalServer', process_name:'str') -> 'intlist':
    """ Returns the processes of the server whose name, as the server sets it, is the given one.
    """
    process:'any_' = server.process
    out:'intlist' = []

    for pid in get_process_tree_pids(process.pid):

        path = ModuleCtx.Proc_Comm_Path.format(pid)

        try:
            with open(path) as comm_file:
                name = comm_file.read()
        except FileNotFoundError:
            continue

        name = name.strip()

        if name == process_name:
            out.append(pid)

    return out

# ################################################################################################################################

def _resume_processes(server:'LocalServer') -> 'None':
    """ Sends SIGCONT to every process of the server, so that a frozen process receives the signals that end it.
    """
    process:'any_' = server.process

    for pid in get_process_tree_pids(process.pid):
        try:
            os.kill(pid, signal.SIGCONT)
        except ProcessLookupError:
            pass

# ################################################################################################################################

def _stop_under_recorder(server:'LocalServer') -> 'None':
    """ Kills every process of the server under a recorder and waits for the recorder to exit.
    """
    process:'any_' = server.process

    for pid in get_process_tree_pids(process.pid):
        if pid != process.pid:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    _ = process.wait(ModuleCtx.Recorder_Exit_Timeout)

# ################################################################################################################################

def stop_local_server(server:'LocalServer') -> 'None':
    """ Stops every process of the server, removes its environment and releases its ports.
    """
    if server.process:
        _resume_processes(server)

        # A recorder writes its output once the processes of the server under it have exited
        if get_command_prefix():
            _stop_under_recorder(server)

    server.state.cleanup()

    if server.stream_thread:
        server.stream_thread.join(ModuleCtx.Stream_Join_Timeout)

    if server.server_port:
        server.server_port.release()

    server.broker_port.release()
    server.mllp_port.release()

# ################################################################################################################################
# ################################################################################################################################
