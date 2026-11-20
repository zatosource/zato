# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The warm server that an active-standby node keeps on a host without an active server. The test acts as the node -
# it creates the activation FIFO, spawns the server by the command of the node with the path of the FIFO and without
# a generation, confirms that the waiting server holds nothing that the active server shares, and writes the generation.

# stdlib
import errno
import logging
import os
import re
import socket
import time

# Zato
from local_server import create_local_server, is_answering, next_generation, read_generation, spawn_warm_local_server, \
    stop_local_server, wait_for_answer
from zato.common.test.pubsub_database import connect
from zato.common.test.process_util import get_process_tree_pids
from zato.common.test.reservation import reserve_port, start_on_reserved_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from local_server import LocalServer
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, intset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The purpose under which the ports of the server are reserved
    Port_Purpose = 'ha-postgresql-local-warm-server'

    # The name of the FIFO in the directory of the server, the same as ACTIVATION_FIFO_NAME of zato_ha_core
    Activation_FIFO_Name = 'ha-activation.fifo'
    Activation_FIFO_Mode = 0o600

    # The entries of the output of the server that report the wait, its outcome and the startup hook
    Waiting_Pattern  = re.compile(r' - Waiting for activation through `')
    Activated_Prefix = 'Activated under generation'
    Failed_Pattern   = re.compile(r' - Activation failed -> Generation `[^`]*` received through `[^`]*` is not an integer')
    Hook_Pattern     = re.compile(r'Default startup callable entering phase')
    Raised_Prefix    = ' - Pub/sub generation raised -> '
    Raised_Template  = Raised_Prefix + '{}, owner:'

    # The startup hook that the server is configured with, which logs each phase that it enters
    Hook_Conf_Pattern = re.compile(r'^(startup_callable\s*=).*$', re.MULTILINE)
    Hook_Name = 'zato.server.startup_callable.default_callable'
    Server_Conf_Path = os.path.join('config', 'repo', 'server.conf')

    # How long the server may take to reach its wait, and how often its output is read meanwhile
    Wait_Timeout = 120.0
    Wait_Interval = 0.05

    # How long the waiting server is observed, and how much CPU time all of its processes may use meanwhile, in seconds
    Observation_Time = 2.0
    Max_Waiting_CPU_Time = 0.1

    # How long the delivery of the generation may be retried while the server has not opened the FIFO yet
    Delivery_Timeout = 10.0

    # How long a server that received an invalid generation may take to exit
    Exit_Timeout = 30.0

    # The line that is not a generation
    Invalid_Generation = 'not-a-generation'

    # The positions of the CPU times of a process in /proc/<pid>/stat, counted after the name of the process
    Stat_User_Time_Index   = 11
    Stat_System_Time_Index = 12

    # The client backends of the database of the session other than the one that lists them
    Backends_Query = """
        select pid from pg_stat_activity
        where datname = current_database()
        and backend_type = 'client backend'
        and pid <> pg_backend_pid()
    """

# ################################################################################################################################
# ################################################################################################################################

def _enable_startup_hook(server_dir:'str') -> 'None':
    """ Configures the server with a startup hook that logs each phase of the start that it enters.
    """
    path = os.path.join(server_dir, ModuleCtx.Server_Conf_Path)

    with open(path) as conf_file:
        content = conf_file.read()

    content = ModuleCtx.Hook_Conf_Pattern.sub(rf'\g<1>{ModuleCtx.Hook_Name}', content)

    with open(path, 'w') as conf_file:
        _ = conf_file.write(content)

# ################################################################################################################################

def _new_activation_path(server_dir:'str') -> 'str':
    """ Creates a new activation FIFO in the directory of the server, removing the one of a previous start.
    """
    out = os.path.join(server_dir, ModuleCtx.Activation_FIFO_Name)

    if os.path.exists(out):
        os.unlink(out)

    os.mkfifo(out, ModuleCtx.Activation_FIFO_Mode)

    return out

# ################################################################################################################################

def _has_line(server:'LocalServer', pattern:'re.Pattern[str]') -> 'bool':
    out = False

    for line in server.output:
        if pattern.search(line):
            out = True
            break

    return out

# ################################################################################################################################

def _has_text(server:'LocalServer', text:'str') -> 'bool':
    out = False

    for line in server.output:
        if text in line:
            out = True
            break

    return out

# ################################################################################################################################

def _wait_for_waiting(server:'LocalServer') -> 'None':
    """ Waits until the server reports that it waits for its activation.
    """
    process:'any_' = server.process
    deadline = time.monotonic() + ModuleCtx.Wait_Timeout

    while not _has_line(server, ModuleCtx.Waiting_Pattern):

        if process.poll() is not None:
            raise Exception(f'Server exited with {process.returncode} before it reached its wait')

        if time.monotonic() > deadline:
            raise Exception(f'Server did not reach its wait within {ModuleCtx.Wait_Timeout}s')

        time.sleep(ModuleCtx.Wait_Interval)

# ################################################################################################################################

def _deliver(activation_path:'str', line:'str') -> 'None':
    """ Writes a line to the activation FIFO as the node does, retrying while the server has not opened it for reading.
    """
    data = line.encode('utf8')
    deadline = time.monotonic() + ModuleCtx.Delivery_Timeout

    while True:
        try:
            descriptor = os.open(activation_path, os.O_WRONLY | os.O_NONBLOCK)

        # The server has not opened the FIFO yet ..
        except OSError as e:
            if e.errno != errno.ENXIO:
                raise
            if time.monotonic() > deadline:
                raise Exception(f'Server did not open {activation_path} within {ModuleCtx.Delivery_Timeout}s')
            time.sleep(ModuleCtx.Wait_Interval)

        # .. and once it has, the line is written in full.
        else:
            try:
                _ = os.write(descriptor, data)
            finally:
                os.close(descriptor)
            break

# ################################################################################################################################

def _get_cpu_time(server:'LocalServer') -> 'float':
    """ Returns the CPU time that all the processes of the server used so far, in seconds.
    """
    process:'any_' = server.process
    ticks_per_second = os.sysconf('SC_CLK_TCK')
    ticks = 0

    for pid in get_process_tree_pids(process.pid):

        with open(f'/proc/{pid}/stat') as stat_file:
            stat = stat_file.read()

        _, _, after_name = stat.rpartition(')')
        fields = after_name.split()

        user_ticks = int(fields[ModuleCtx.Stat_User_Time_Index])
        system_ticks = int(fields[ModuleCtx.Stat_System_Time_Index])

        ticks += user_ticks + system_ticks

    out = ticks / ticks_per_second
    return out

# ################################################################################################################################

def _get_backend_pids(database:'PubSubDatabase') -> 'intset':
    """ Returns the processes of PostgreSQL that serve the clients of the database of the session.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute(ModuleCtx.Backends_Query)
        rows:'any_' = cursor.fetchall()
    finally:
        connection.close()

    out:'intset' = set()

    for row in rows:
        pid = row[0]
        out.add(pid)

    return out

# ################################################################################################################################

def _is_port_free(port:'int') -> 'bool':
    """ Returns whether nothing listens on the port.
    """
    try:
        connection = socket.create_connection(('127.0.0.1', port))
    except ConnectionRefusedError:
        out = True
    else:
        connection.close()
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_warm_server_waits_and_starts_on_activation(pubsub_database:'PubSubDatabase') -> 'None':
    """ A warm server waits without a port, without a connection to the Zato database, without a startup hook
    and without CPU use, and once it receives the generation, it starts under it and answers /zato/ping.
    """
    server = create_local_server(pubsub_database)
    _enable_startup_hook(server.server_dir)

    def start(port:'int') -> 'float':

        # The test acts as the node - it creates the FIFO and spawns the server without a generation ..
        activation_path = _new_activation_path(server.server_dir)
        backends_before = _get_backend_pids(pubsub_database)

        spawn_warm_local_server(server, port, activation_path)
        _wait_for_waiting(server)

        # .. the waiting server is observed for a while ..
        cpu_time_before = _get_cpu_time(server)
        time.sleep(ModuleCtx.Observation_Time)
        cpu_time_after = _get_cpu_time(server)
        cpu_time_waiting = cpu_time_after - cpu_time_before

        logger.info('Warm server CPU time while waiting -> %.3fs', cpu_time_waiting)

        process:'any_' = server.process
        backends_waiting = _get_backend_pids(pubsub_database)
        new_backends = backends_waiting - backends_before

        # .. during which it is still waiting, uses no CPU, binds no port, has no connection
        # to the Zato database and runs no startup hook ..
        assert process.poll() is None
        assert not _has_text(server, ModuleCtx.Activated_Prefix)
        assert cpu_time_waiting < ModuleCtx.Max_Waiting_CPU_Time, cpu_time_waiting
        assert _is_port_free(port)
        assert not is_answering(server.ping_url, ModuleCtx.Wait_Interval)
        assert new_backends == set(), new_backends
        assert not _has_line(server, ModuleCtx.Hook_Pattern)

        # .. the test delivers the generation as the node does ..
        generation = next_generation(pubsub_database)
        _deliver(activation_path, f'{generation}\n')

        # .. and the server starts under it.
        out = wait_for_answer(server)

        raised_text = ModuleCtx.Raised_Template.format(generation)

        assert _has_text(server, f'{ModuleCtx.Activated_Prefix} {generation}')
        assert _has_text(server, raised_text)
        assert _has_line(server, ModuleCtx.Hook_Pattern)

        return out

    try:
        started = start_on_reserved_port(ModuleCtx.Port_Purpose, start)
        server.server_port = started.reservation

        logger.info('Warm server first answer after the spawn -> %.3fs', started.result)

    finally:
        stop_local_server(server)

# ################################################################################################################################

def test_warm_server_exits_on_invalid_generation(pubsub_database:'PubSubDatabase') -> 'None':
    """ A warm server that receives a line that is not an integer exits with a non-zero code
    before it connects to the Zato database.
    """
    server = create_local_server(pubsub_database)
    port = reserve_port(ModuleCtx.Port_Purpose)
    server.server_port = port

    try:
        stored_generation = read_generation(pubsub_database)

        # The server waits ..
        activation_path = _new_activation_path(server.server_dir)
        spawn_warm_local_server(server, port.port, activation_path)
        _wait_for_waiting(server)

        # .. the test writes a line that is not a generation ..
        _deliver(activation_path, f'{ModuleCtx.Invalid_Generation}\n')

        process:'any_' = server.process
        returncode = process.wait(ModuleCtx.Exit_Timeout)

        stream_thread:'any_' = server.stream_thread
        stream_thread.join(ModuleCtx.Exit_Timeout)

        generation_after = read_generation(pubsub_database)

        # .. and the server exits with an error, without a raise of the generation.
        assert returncode != 0
        assert _has_line(server, ModuleCtx.Failed_Pattern)
        assert not _has_text(server, ModuleCtx.Raised_Prefix)
        assert generation_after == stored_generation

    finally:
        stop_local_server(server)

# ################################################################################################################################
# ################################################################################################################################
