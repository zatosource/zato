# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import time

# Zato
from arbiter_common import Condition_Timeout, get_pids, none_running, Region_Config, slot_replaced, start_arbiter, \
    stop_arbiter, Tested_Slot, wait_until
from zato.server.arbiter_config import ModuleCtx
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import callable_

    callable_ = callable_
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

def _get_process_name(pid:'int') -> 'str':
    with open(f'/proc/{pid}/comm') as comm_file:
        out = comm_file.read().rstrip('\n')

    return out

# ################################################################################################################################

def _new_writer_main(pid_path:'Path') -> 'callable_':
    """ Returns the main function of a writer that records its PID and waits until it is terminated.
    """
    def writer_main(_listen_fd:'int') -> 'None':
        _ = pid_path.write_text(str(os.getpid()))

        while True:
            time.sleep(Condition_Timeout)

    return writer_main

# ################################################################################################################################

def _has_pid(pid_path:'Path') -> 'bool':
    out = pid_path.exists() and pid_path.read_text() != ''
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_every_process_carries_the_name_of_its_role(tmp_path:'Path') -> 'None':
    control_dir = tmp_path / 'control'
    control_dir.mkdir()

    pid_path = tmp_path / 'writer-pid'

    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'serve', str(control_dir), _new_writer_main(pid_path))
    pids = get_pids(region)

    assert wait_until(_has_pid, (pid_path,))
    writer_pid = int(pid_path.read_text())

    # The arbiter, the writer and the worker of each slot list under their roles ..
    assert _get_process_name(arbiter.pid) == ModuleCtx.Process_Name_Arbiter
    assert _get_process_name(writer_pid) == ModuleCtx.Process_Name_Writer

    for slot, pid in enumerate(pids):
        assert _get_process_name(pid) == ModuleCtx.Process_Name_Worker.format(slot)

    # .. and the replacement of a terminated worker lists under the slot of its predecessor.
    os.kill(pids[Tested_Slot], signal.SIGKILL)
    assert wait_until(slot_replaced, (region, Tested_Slot, 2))

    replacement = region.slot_pid(Tested_Slot)
    assert _get_process_name(replacement) == ModuleCtx.Process_Name_Worker.format(Tested_Slot)

    pids = get_pids(region)
    stop_arbiter(arbiter, pids, str(control_dir))

    assert none_running([writer_pid])

# ################################################################################################################################
# ################################################################################################################################
