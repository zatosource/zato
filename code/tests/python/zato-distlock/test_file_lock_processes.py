# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import traceback
from multiprocessing import get_context

# Zato
from zato.distlock import FCNTLLock

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.synchronize import Event
    from pathlib import Path

    Event = Event
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The processes are forked, as the worker and the config process are forked from the arbiter
    Context = get_context('fork')

    Process_Count = 4

    OS_User_Name = 'zato'
    Namespace = 'test'
    Name = 'test.file-lock'

    # How many holds each process begins, all of them starting together, so that they contend for the lock
    Holds_Per_Process = 250

    # How long the test waits for a process, in seconds
    Join_Timeout = 60.0

    Entry = 'E'
    Leave = 'L'

# ################################################################################################################################
# ################################################################################################################################

def _new_lock() -> 'FCNTLLock':
    out = FCNTLLock(ModuleCtx.OS_User_Name, ModuleCtx.Namespace, ModuleCtx.Name, 0, 0, 0, False)
    return out

# ################################################################################################################################

def _remove_lock_file() -> 'None':
    """ Removes the file of the lock name, which a release leaves in the temporary directory.
    """
    lock = _new_lock()
    info = lock.acquire()

    assert info.acquired
    assert lock.tmp_file_name is not None

    lock.release()
    os.remove(lock.tmp_file_name)

# ################################################################################################################################

def _contend(log_path:'str', start:'Event') -> 'None':
    """ Acquires and releases the lock in a loop, writing an entry line and a leave line for each hold.
    """
    exit_code = 1

    try:
        log_fd = os.open(log_path, os.O_WRONLY | os.O_APPEND)
        pid = os.getpid()
        holds = 0

        _ = start.wait()

        while holds < ModuleCtx.Holds_Per_Process:
            lock = _new_lock()
            info = lock.acquire()

            if info.acquired:
                _ = os.write(log_fd, f'{ModuleCtx.Entry} {pid}\n'.encode())
                _ = os.write(log_fd, f'{ModuleCtx.Leave} {pid}\n'.encode())
                lock.release()
                holds += 1

            # A lock that is not acquired leaves its file to the holder
            else:
                lock.tmp_file.close()

        os.close(log_fd)
        exit_code = 0

    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################

def test_no_two_processes_hold_one_lock_name_at_once(tmp_path:'Path') -> 'None':
    log_path = str(tmp_path / 'holds.log')
    open(log_path, 'w').close()

    processes = []
    start = ModuleCtx.Context.Event()

    for _ in range(ModuleCtx.Process_Count):
        process = ModuleCtx.Context.Process(target=_contend, args=(log_path, start))
        processes.append(process)

    for process in processes:
        process.start()

    start.set()

    for process in processes:
        process.join(ModuleCtx.Join_Timeout)
        assert process.exitcode == 0

    # An entry line that follows the entry line of another holder is a time when two processes held the lock at once
    holder = ''
    holds = 0
    overlaps = 0

    with open(log_path) as log_file:
        for line in log_file:
            kind, pid = line.split()

            if kind == ModuleCtx.Entry:
                holds += 1

                if holder:
                    overlaps += 1

                holder = pid

            elif pid == holder:
                holder = ''

    assert holds == ModuleCtx.Process_Count * ModuleCtx.Holds_Per_Process
    assert overlaps == 0

    _remove_lock_file()

# ################################################################################################################################

def test_a_released_lock_keeps_its_file() -> 'None':
    lock = _new_lock()
    info = lock.acquire()

    assert info.acquired

    lock.release()

    # The next holder of the name opens and locks the same file
    assert lock.tmp_file_name is not None
    assert os.path.exists(lock.tmp_file_name)

    next_lock = _new_lock()
    next_info = next_lock.acquire()

    assert next_info.acquired
    assert next_lock.tmp_file_name == lock.tmp_file_name

    next_lock.release()
    _remove_lock_file()

# ################################################################################################################################
# ################################################################################################################################
