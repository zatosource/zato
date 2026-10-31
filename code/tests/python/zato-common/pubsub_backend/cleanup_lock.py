# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3
import sys
from tempfile import TemporaryFile
from time import monotonic

# gevent
from gevent import sleep

# Zato
from cleanup import set_expired
from common import delete_all_rows, get_message_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import get_pubsub_db_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

_topic_name = 'pubsub.backend.test.cleanup.lock'
_sub_key = 'zpsk.test.cleanup.lock'

# How many expired messages the sweep must delete.
_expired_count = 3

# How long the write lock is held, in seconds - longer than the busy timeout of 5 seconds,
# so the first attempt of the sweep cannot obtain the lock.
_lock_hold_seconds = 7

# How long the cleanup process may take at most once the lock is released, in seconds.
_sweep_deadline_seconds = 30

# How often the run checks whether the cleanup process has ended, in seconds.
_sweep_poll_seconds = 0.1

# What the cleanup process logs each time it postpones a sweep.
_postponed_message = b'Sweep postponed, the database is locked'

# ################################################################################################################################
# ################################################################################################################################

def run_cleanup_lock_scenario() -> 'None':
    """ The cleanup process against a database whose write lock another connection holds for longer
    than the busy timeout - the process postpones the sweep instead of ending, and once the lock is
    released, the sweep completes and deletes every expired message.
    """
    delete_all_rows()

    backend = SQLPubSubBackend()
    backend.subscribe(_sub_key, _topic_name)

    expired_msg_ids:'strlist' = []

    for index in range(_expired_count):
        result = backend.publish(_topic_name, f'cleanup-lock-{index}')
        expired_msg_ids.append(result.msg_id)

    set_expired(expired_msg_ids)

    # Another writer holds the write lock ..
    db_path = get_pubsub_db_path()

    lock_connection = sqlite3.connect(db_path, isolation_level=None)
    _ = lock_connection.execute('begin immediate')

    # .. while the cleanup process runs as its own operating system process, spawned without a fork,
    # .. which a process full of greenlets must never issue ..
    sweep_args = [sys.executable, '-m', 'zato.common.pubsub.sql.cleanup', '--once']

    with TemporaryFile() as sweep_output:

        file_actions = [
            (os.POSIX_SPAWN_DUP2, sweep_output.fileno(), 1),
            (os.POSIX_SPAWN_DUP2, sweep_output.fileno(), 2),
        ]

        sweep_pid = os.posix_spawn(sys.executable, sweep_args, os.environ, file_actions=file_actions)

        # .. for longer than the busy timeout of the sweep ..
        sleep(_lock_hold_seconds)

        _ = lock_connection.execute('rollback')
        lock_connection.close()

        # .. after which the sweep obtains the lock and completes.
        deadline = monotonic() + _sweep_deadline_seconds

        while True:
            done_pid, wait_status = os.waitpid(sweep_pid, os.WNOHANG)
            if done_pid:
                break
            assert monotonic() < deadline, 'The cleanup process did not complete'
            sleep(_sweep_poll_seconds)

        _ = sweep_output.seek(0)
        output = sweep_output.read()

    assert os.waitstatus_to_exitcode(wait_status) == 0, output
    assert _postponed_message in output, output

    message_rows = get_message_rows(_topic_name)
    assert len(message_rows) == 0, message_rows

# ################################################################################################################################
# ################################################################################################################################
