# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal

# Zato
from arbiter_common import config_started, Probe, Region_Config, start_arbiter, stop_arbiter, wait_until, worker_replaced
from zato.server.arbiter_config import ModuleCtx
from zato.server.arbiter_config_process import ConfigProcessCtx
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

def _get_process_name(pid:'int') -> 'str':
    with open(f'/proc/{pid}/comm') as comm_file:
        out = comm_file.read().rstrip('\n')

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_every_process_carries_the_name_of_its_role(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()
    arbiter = start_arbiter(region, probe, 'serve_with_config', tmp_dir)

    assert config_started(probe)

    # The arbiter, the config process and the worker list under their roles ..
    assert _get_process_name(arbiter.pid) == ModuleCtx.Process_Name_Arbiter
    assert _get_process_name(probe.config_pid.value) == ConfigProcessCtx.Process_Name
    assert _get_process_name(probe.worker_pid()) == ModuleCtx.Process_Name_Worker

    # .. and the replacement of a terminated worker lists under the same role.
    os.kill(probe.worker_pid(), signal.SIGKILL)
    assert wait_until(worker_replaced, (probe, 2))

    assert _get_process_name(probe.worker_pid()) == ModuleCtx.Process_Name_Worker

    stop_arbiter(arbiter, [probe.worker_pid(), probe.config_pid.value], tmp_dir)

# ################################################################################################################################
# ################################################################################################################################
