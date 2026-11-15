# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import time
from multiprocessing import get_context
from socket import AF_UNIX, socket, SOCK_STREAM

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from arbiter_common import Condition_Timeout, get_pids, Grace_Metric, metric_reached, none_running, Published_Metric, \
    Region_Config, Slot_Count, start_arbiter, stop_arbiter, wait_until, Writer_Message_Count
from writer_common import Topic_Name
from zato.common.db_env.engine import set_process_queue
from zato.common.db_env.process_queue import ProcessQueue
from zato.common.pubsub.sql.config import get_pubsub_engine, ModuleCtx
from zato.common.pubsub.sql.schema import delivery_table, message_table, topic_sub_table
from zato.common.pubsub.writer_process.handlers import run_writer
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from pytest import MonkeyPatch
    from zato.common.typing_ import callable_, intlist

    callable_ = callable_
    intlist = intlist
    MonkeyPatch = MonkeyPatch
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# The database is prepared and read in processes of their own, so that this process holds no engine and no checkpoint thread
# that the arbiter or any process forked later would inherit
_context = get_context('fork')

_sub_key = 'sk-1'

# The writer queue of the pub/sub file
_pubsub_queue = 0

# How many publications have succeeded when the test terminates the writer
_published_before_kill = 10

# ################################################################################################################################
# ################################################################################################################################

def _subscribe() -> 'None':
    with get_pubsub_engine().begin() as connection:
        _ = connection.execute(topic_sub_table.insert(), {'sub_key': _sub_key, 'topic_name': Topic_Name})

# ################################################################################################################################

def _check_message_count(message_count:'int') -> 'None':
    message_count_query = select(func.count()).select_from(message_table)
    distinct_query = select(func.count(func.distinct(message_table.c.msg_id)))
    delivery_count_query = select(func.count()).select_from(delivery_table)

    with get_pubsub_engine().connect() as connection:
        assert connection.execute(message_count_query).scalar_one() == message_count
        assert connection.execute(distinct_query).scalar_one() == message_count
        assert connection.execute(delivery_count_query).scalar_one() == message_count

# ################################################################################################################################

def _new_writer_main(region:'SharedRegion', pid_path:'Path', address_path:'Path') -> 'callable_':
    """ Returns the main function of the writer, which records the PID of each writer process and the address
    of its listening socket before it serves, taking its turns in the queue of the pub/sub file.
    """
    def writer_main(listen_fd:'int') -> 'None':
        with open(pid_path, 'a') as pid_file:
            _ = pid_file.write(f'{os.getpid()}\n')

        with socket(AF_UNIX, SOCK_STREAM, fileno=os.dup(listen_fd)) as listener:
            _ = address_path.write_text(listener.getsockname())

        process_queue = ProcessQueue(region, _pubsub_queue, region.writer_place, Condition_Timeout)
        set_process_queue(get_pubsub_engine(), process_queue)

        run_writer(listen_fd)

    return writer_main

# ################################################################################################################################

def _new_holding_writer_main(region:'SharedRegion', pid_path:'Path') -> 'callable_':
    """ Returns the main function of a writer that takes the turn of the pub/sub file, records its PID once it holds
    the turn, and holds the turn until it is terminated.
    """
    def writer_main(_listen_fd:'int') -> 'None':
        _ = region.queue_enter(_pubsub_queue, region.writer_place)
        assert region.queue_poll(_pubsub_queue, region.writer_place)

        with open(pid_path, 'a') as pid_file:
            _ = pid_file.write(f'{os.getpid()}\n')

        while True:
            time.sleep(Condition_Timeout)

    return writer_main


# ################################################################################################################################

def _get_writer_pids(pid_path:'Path') -> 'intlist':
    out:'intlist' = []

    if pid_path.exists():
        for line in pid_path.read_text().splitlines():
            out.append(int(line))

    return out

# ################################################################################################################################

def _has_writer_count(pid_path:'Path', count:'int') -> 'bool':
    writer_pids = _get_writer_pids(pid_path)

    out = len(writer_pids) == count
    return out

# ################################################################################################################################

def _published_at_least(region:'SharedRegion', count:'int') -> 'bool':
    out = region.metric_sum(Published_Metric) >= count
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_publications_of_every_worker_survive_a_terminated_writer(tmp_path:'Path', monkeypatch:'MonkeyPatch') -> 'None':
    monkeypatch.setenv(ModuleCtx.Env_Path, str(tmp_path / 'pubsub.db'))

    control_dir = tmp_path / 'control'
    control_dir.mkdir()

    pid_path = tmp_path / 'writer-pids'
    address_path = tmp_path / 'writer-address'

    # The topic has one subscriber ..
    process = _context.Process(target=_subscribe)
    process.start()
    process.join(Condition_Timeout)

    assert process.exitcode == 0

    # .. the arbiter forks the writer and the workers, each of which publishes through the writer ..
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'publish_to_writer', str(control_dir), _new_writer_main(region, pid_path, address_path))
    pids = get_pids(region)

    # .. every worker inherited the grace period of the traces ..
    assert wait_until(metric_reached, (region, Grace_Metric, Slot_Count))

    # .. the writer is terminated while the workers publish ..
    assert wait_until(_has_writer_count, (pid_path, 1))
    first_writer = _get_writer_pids(pid_path)[0]

    assert wait_until(_published_at_least, (region, _published_before_kill))
    os.kill(first_writer, signal.SIGKILL)

    # .. the arbiter starts the next writer, and every publication succeeds ..
    assert wait_until(_has_writer_count, (pid_path, 2))

    message_count = Slot_Count * Writer_Message_Count
    assert wait_until(metric_reached, (region, Published_Metric, message_count))

    # .. and once the arbiter stopped, no writer remains and the directory of its socket is removed.
    writer_pids = _get_writer_pids(pid_path)
    stop_arbiter(arbiter, pids, str(control_dir))

    address = address_path.read_text()
    socket_dir = os.path.dirname(address)

    assert none_running(writer_pids)
    assert not os.path.exists(socket_dir)

    # Each message is in the database once, with its one delivery row
    process = _context.Process(target=_check_message_count, args=(message_count,))
    process.start()
    process.join(Condition_Timeout)

    assert process.exitcode == 0

# ################################################################################################################################

def test_the_place_of_a_terminated_writer_is_withdrawn(tmp_path:'Path') -> 'None':
    control_dir = tmp_path / 'control'
    control_dir.mkdir()

    pid_path = tmp_path / 'writer-pids'

    # The writer holds the turn of the pub/sub file when it is terminated ..
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'serve', str(control_dir), _new_holding_writer_main(region, pid_path))
    pids = get_pids(region)

    assert wait_until(_has_writer_count, (pid_path, 1))
    first_writer = _get_writer_pids(pid_path)[0]

    os.kill(first_writer, signal.SIGKILL)

    # .. and the arbiter withdraws its place, so that the next writer takes the turn of the file anew.
    assert wait_until(_has_writer_count, (pid_path, 2))

    writer_pids = _get_writer_pids(pid_path)
    stop_arbiter(arbiter, pids, str(control_dir))

    assert none_running(writer_pids)

# ################################################################################################################################

def test_the_writer_outlasts_the_workers_under_killpg(tmp_path:'Path', monkeypatch:'MonkeyPatch') -> 'None':
    monkeypatch.setenv(ModuleCtx.Env_Path, str(tmp_path / 'pubsub.db'))

    control_dir = tmp_path / 'control'
    control_dir.mkdir()

    pid_path = tmp_path / 'writer-pids'
    address_path = tmp_path / 'writer-address'

    process = _context.Process(target=_subscribe)
    process.start()
    process.join(Condition_Timeout)

    assert process.exitcode == 0

    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'publish_on_sigterm', str(control_dir), _new_writer_main(region, pid_path, address_path))
    pids = get_pids(region)

    assert wait_until(_has_writer_count, (pid_path, 1))
    writer_pid = _get_writer_pids(pid_path)[0]

    # SIGTERM reaches the arbiter, every worker and the writer at once, as killpg delivers it to the process group ..
    os.kill(arbiter.pid, signal.SIGTERM)

    for pid in pids:
        os.kill(pid, signal.SIGTERM)

    os.kill(writer_pid, signal.SIGTERM)

    # .. and every worker publishes its message while it drains, before the arbiter exits.
    arbiter.join(Condition_Timeout)

    assert arbiter.exitcode == 0
    assert region.metric_sum(Published_Metric) == Slot_Count
    assert none_running([*pids, writer_pid])

# ################################################################################################################################
# ################################################################################################################################
