# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The start of a server under the generation of an active-standby node, by the command that the node runs, measured
# from the spawn of the command to the first answer of /zato/ping, together with the stages of the start that the log
# of the server reports. A node labels its pod only after that answer, so this time is part of every failover.

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
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_pubsub import SessionState, get_server_environment, patch_server_conf, \
     run_quickstart_and_enmasse
from zato.common.test.ha_limits import HALimits
from zato.common.test.perf_report import report_result, start_measurement
from zato.common.test.process_util import get_process_tree_pids
from zato.common.test.pubsub_database import connect
from zato.common.test.reservation import reserve_port
from zato.common.test.takeover import ModuleCtx as TakeoverCtx
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

stage_list   = list['Stage']
strfloatdict = dict[str, float]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variable through which an active-standby node passes its generation to its server
    Env_HA_Generation = 'Zato_HA_Generation'

    # The purpose under which the ports of the server are reserved
    Port_Purpose = 'ha-postgresql-local-server'

    # How long the start may take, from the spawn of the command to the first answer of /zato/ping
    Start_Limit = HALimits.Server_Start

    # How long the test waits for the first answer before it gives up
    Start_Timeout = 120.0

    # How long after the first answer the stages that the server reports later may take
    Stage_Timeout = 30.0

    # How often the readiness of the server is checked, and how long each check may take
    Ping_Interval = 0.02
    Ping_Timeout = 0.25

    # How far above the stored generation the node of the test begins
    Generation_Step = 100

    # The prefix of the quickstart directory, the name of the copy of its log and the name of the logger of the session
    Quickstart_Prefix = 'zato_ha_local_start_'
    Log_Copy_Name = 'zato-ha-local-start.log'
    Logger_Name = 'zato.test.ha_postgresql_local'

    # How long the stream of the output may take to finish once the server has been killed
    Stream_Join_Timeout = 10.0

    # The variable with the command of a recorder that the server is started through, e.g. py-spy of bin/perf-run,
    # and how long the recorder may take to write its output once the server has exited
    Env_Command_Prefix = 'Zato_Test_Server_Command_Prefix'
    Recorder_Exit_Timeout = 60.0

    # The name under which the figures of the start are recorded
    Result_Name = 'Server start'

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

def _new_stage(name:'str', pattern:'str') -> 'Stage':
    """ Returns a stage that has not been reached yet.
    """
    out = Stage()
    out.name = name
    out.pattern = re.compile(pattern)
    out.elapsed = None

    return out

# ################################################################################################################################

def _new_stages() -> 'stage_list':
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

def _read_generation(database:'PubSubDatabase') -> 'int':
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

def _stream_output(process:'subprocess.Popen[bytes]', spawned_at:'float', stages:'stage_list') -> 'None':
    """ Logs each line of the output of the server and records when each stage was first reported.
    """
    stdout:'any_' = process.stdout

    for line in iter(stdout.readline, b''):
        text = line.decode('utf-8', errors='replace').rstrip()
        elapsed = time.monotonic() - spawned_at

        logger.debug('[SERVER %6.3fs] %s', elapsed, text)

        for stage in stages:
            if stage.elapsed is None:
                if stage.pattern.search(text):
                    stage.elapsed = elapsed

# ################################################################################################################################

def _is_answering(ping_url:'str') -> 'bool':
    """ Whether /zato/ping of the server answers with 200.
    """
    request = Request(ping_url, method='GET')

    try:
        with urlopen(request, timeout=ModuleCtx.Ping_Timeout) as response:
            out = response.status == OK
    except (OSError, URLError):
        out = False

    return out

# ################################################################################################################################

def _wait_for_answer(process:'subprocess.Popen[bytes]', ping_url:'str', spawned_at:'float') -> 'float':
    """ Returns how long after the spawn /zato/ping first answered with 200.
    """
    deadline = spawned_at + ModuleCtx.Start_Timeout

    while time.monotonic() < deadline:

        if _is_answering(ping_url):
            out = time.monotonic() - spawned_at
            return out

        if process.poll() is not None:
            raise Exception(f'Server exited with {process.returncode} before it answered')

        time.sleep(ModuleCtx.Ping_Interval)

    raise Exception(f'Server did not answer within {ModuleCtx.Start_Timeout}s')

# ################################################################################################################################

def _wait_for_stages(stages:'stage_list') -> 'None':
    """ Waits until every stage was reported, including those that the server reports after its first answer.
    """
    deadline = time.monotonic() + ModuleCtx.Stage_Timeout

    for stage in stages:
        while stage.elapsed is None:
            if time.monotonic() > deadline:
                raise Exception(f'Stage {stage.name} not reported within {ModuleCtx.Stage_Timeout}s')
            time.sleep(ModuleCtx.Ping_Interval)

# ################################################################################################################################

def _stage_figures(stages:'stage_list') -> 'strfloatdict':
    """ Returns how long after the spawn each stage was reported, by the name of the stage.
    """
    out:'strfloatdict' = {}

    for stage in stages:
        out[stage.name] = cast_('float', stage.elapsed)

    return out

# ################################################################################################################################

def _get_command_prefix() -> 'strlist':
    """ Returns the command of the recorder that the server is started through, or an empty list without one.
    """
    prefix = os.environ.get(ModuleCtx.Env_Command_Prefix, '')

    out = shlex.split(prefix)
    return out

# ################################################################################################################################

def _stop_under_recorder(process:'subprocess.Popen[bytes]') -> 'None':
    """ Kills every process of the server under a recorder and waits for the recorder to exit.
    """
    for pid in get_process_tree_pids(process.pid):
        if pid != process.pid:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    _ = process.wait(ModuleCtx.Recorder_Exit_Timeout)

# ################################################################################################################################
# ################################################################################################################################

def test_server_start(pubsub_database:'PubSubDatabase') -> 'None':
    """ A server started by `zato start <dir> --fg` with a node's generation answers /zato/ping within Start_Limit,
    and its log reports every stage of its start.
    """
    state = SessionState(ModuleCtx.Logger_Name, ModuleCtx.Log_Copy_Name)

    server_port = reserve_port(ModuleCtx.Port_Purpose)
    broker_port = reserve_port(ModuleCtx.Port_Purpose)
    mllp_port = reserve_port(ModuleCtx.Port_Purpose)

    process = None
    stream_thread = None

    try:

        # The environment of the server is created on the database of the session ..
        work_dir_env:'strstrdict' = dict(pubsub_database.env)

        invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()
        zato_bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

        server_dir = run_quickstart_and_enmasse(
            state=state,
            logger=logger,
            zato_bin=zato_bin,
            invoke_password=invoke_password,
            rendered_yaml='',
            quickstart_prefix=ModuleCtx.Quickstart_Prefix,
            extra_env=work_dir_env,
            log_to_files=False,
        )

        patch_server_conf(server_dir, server_port.port, True)

        # .. the server receives the generation of a node above the one that the database holds ..
        generation = _read_generation(pubsub_database) + ModuleCtx.Generation_Step

        server_env:'strstrdict' = dict(pubsub_database.env)
        server_env[TakeoverCtx.Env_Generation_File] = os.path.join(server_dir, TakeoverCtx.Generation_File_Name)
        server_env[ModuleCtx.Env_HA_Generation] = f'{generation}'

        env = get_server_environment(server_port.port, broker_port.port, mllp_port.port, server_env)

        # .. it is started by the command of the node, through the command of a recorder if one is given ..
        command = [*_get_command_prefix(), zato_bin, 'start', server_dir, '--fg']
        stages = _new_stages()

        spawned_at = time.monotonic()
        spawned_at_epoch = time.time()

        process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        state.server_process = process

        stream_thread = threading.Thread(target=_stream_output, args=(process, spawned_at, stages), daemon=True)
        stream_thread.start()

        # .. and the time to its first answer is what a node waits for before it labels its pod.
        base_url = f'http://127.0.0.1:{server_port.port}'
        ping_url = f'{base_url}/zato/ping'

        answered_after = _wait_for_answer(process, ping_url, spawned_at)
        answered_at_epoch = spawned_at_epoch + answered_after

        # Every stage is reported ..
        _wait_for_stages(stages)

        for stage in stages:
            logger.info('Server start stage %s -> %.3fs', stage.name, stage.elapsed)

        logger.info('Server start first answer -> %.3fs', answered_after)

        # .. the figures of the start are recorded with the settings of the server, which are known once it answers ..
        client = AdminClient(base_url, invoke_password)
        measurement = start_measurement(client, pubsub_database)

        figures = {
            'stages': _stage_figures(stages),
            'first_answer': answered_after,
            'spawned_at_monotonic': spawned_at,
            'window_start': spawned_at_epoch,
            'window_end': answered_at_epoch,
        }

        _ = report_result(measurement, ModuleCtx.Result_Name, figures)

        # .. and the answer came within the limit.
        assert answered_after < ModuleCtx.Start_Limit, answered_after

    finally:

        # A recorder writes its output once the processes of the server under it have exited
        if process and _get_command_prefix():
            _stop_under_recorder(process)

        state.cleanup()

        if stream_thread:
            stream_thread.join(ModuleCtx.Stream_Join_Timeout)

        server_port.release()
        broker_port.release()
        mllp_port.release()

# ################################################################################################################################
# ################################################################################################################################
