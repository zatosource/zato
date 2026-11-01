# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import subprocess
import sys
from time import monotonic

# gevent
from gevent import sleep

# SQLAlchemy
from sqlalchemy import text

# Zato
from profiles import get_profile_limits
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.test.pubsub_database import connect, ModuleCtx
from zato.common.test.pubsub_network import install_idle_limit, read_dropped_packets

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import ManagedDatabase
    from zato.common.typing_ import intset

# ################################################################################################################################
# ################################################################################################################################

# How much longer than the idle limit the connections stay idle, in seconds.
_idle_margin_seconds = 60

# How long the second sweep of the cleanup process may take to complete, and how often its log is read, in seconds.
_sweep_timeout_seconds = 180
_sweep_poll_seconds = 1

# How long the cleanup process may take to stop, in seconds.
_stop_timeout_seconds = 30

# What the cleanup process logs once a sweep completes and when a sweep has to start again.
_sweep_completed = 'Sweep completed'
_sweep_postponed = 'Sweep postponed'

# The backends of the pub/sub role.
_backends_query = "select pid from pg_stat_activity where usename = %s and backend_type = 'client backend'"

# ################################################################################################################################
# ################################################################################################################################

def _read_backends(managed_database:'ManagedDatabase') -> 'intset':
    """ Returns the process identifiers of the backends of pub/sub, read over a new connection of the administrator.
    """
    connection = connect(managed_database.database, is_admin=True)

    try:
        cursor = connection.cursor()
        cursor.execute(_backends_query, (ModuleCtx.Username,))

        out:'intset' = set()
        for row in cursor.fetchall():
            out.add(row[0])

    finally:
        connection.close()

    return out

# ################################################################################################################################

def _read_log(log_path:'str') -> 'str':
    with open(log_path) as log_file:
        out = log_file.read()
    return out

# ################################################################################################################################

def _wait_for_sweeps(log_path:'str', count:'int') -> 'str':
    """ Waits until the cleanup process logged the given number of completed sweeps and returns its log.
    """
    deadline = monotonic() + _sweep_timeout_seconds

    while True:
        out = _read_log(log_path)

        if out.count(_sweep_completed) >= count:
            break

        assert monotonic() < deadline, f'The cleanup process did not complete {count} sweeps -> {out}'

        sleep(_sweep_poll_seconds)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_idle_connections(managed_database:'ManagedDatabase') -> 'None':
    """ The network forgets the connections that stay idle for longer than the limit
    of the service and drops their packets without notifying either end. The pooled connections of a server
    and of the cleanup process outlive the limit through their keepalives and are used again as they are,
    whereas a connection without keepalives within the limit is cut off.
    """
    limits = get_profile_limits()
    idle_seconds = limits.idle_limit_seconds + _idle_margin_seconds

    container_name = managed_database.database.container_name
    install_idle_limit(container_name, limits.idle_limit_seconds)

    # The server takes over the database, so that the cleanup process sweeps it ..
    backend = SQLPubSubBackend()
    backend.take_over()

    engine = get_pubsub_engine()

    with engine.connect() as connection:
        server_pid = connection.execute(text('select pg_backend_pid()')).scalar_one()

    # .. the cleanup process sweeps once at the start and once more after the connections were idle ..
    log_path = os.path.join(managed_database.work_dir, 'cleanup.log')
    interval = f'{idle_seconds}'

    with open(log_path, 'w') as log_file:
        command = [sys.executable, '-m', 'zato.common.pubsub.sql.cleanup', '--interval', interval]
        cleanup = subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT, env=dict(os.environ))

    try:
        _ = _wait_for_sweeps(log_path, 1)

        # .. the connection without keepalives belongs to the administrator, so that its backend
        # .. is not counted among those of pub/sub ..
        control = connect(managed_database.database, is_admin=True)
        control_cursor = control.cursor()
        control_cursor.execute('select 1')

        backends_before = _read_backends(managed_database)
        dropped_before = read_dropped_packets(container_name)

        sleep(idle_seconds)

        # .. the pooled connection of the server is the same one as before the idle time ..
        with engine.connect() as connection:
            server_pid_after = connection.execute(text('select pg_backend_pid()')).scalar_one()

        assert server_pid_after == server_pid, (server_pid, server_pid_after)

        # .. the cleanup process completed its second sweep without starting it again ..
        log = _wait_for_sweeps(log_path, 2)
        assert _sweep_postponed not in log, log

        # .. and on its own connection, because no backend of pub/sub was replaced ..
        backends_after = _read_backends(managed_database)
        assert backends_before <= backends_after, (backends_before, backends_after)

        # .. whereas the connection without keepalives is cut off ..
        is_control_cut = False

        try:
            control_cursor.execute('select 1')
        except Exception:
            is_control_cut = True

        assert is_control_cut, 'The connection without keepalives outlived the idle limit'

        # .. because the network dropped its packets.
        dropped_after = read_dropped_packets(container_name)
        assert dropped_after > dropped_before, (dropped_before, dropped_after)

    finally:
        cleanup.send_signal(signal.SIGTERM)
        _ = cleanup.wait(timeout=_stop_timeout_seconds)

        guard = backend.generation_guard
        if guard:
            guard.uninstall(engine)

# ################################################################################################################################
# ################################################################################################################################
