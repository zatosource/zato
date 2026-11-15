# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from arbiter_common import get_pids, Region_Config, start_arbiter, stop_arbiter, Writes_Metric
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

def test_one_worker_of_all_invokes_the_service_for_a_message_that_every_worker_receives(tmp_path:'Path') -> 'None':
    control_dir = tmp_path / 'control'
    control_dir.mkdir()

    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'receive_control_id', str(control_dir))
    pids = get_pids(region)

    # Every worker reported ready after its check, and the control ID was new to one of them only
    assert region.metric_sum(Writes_Metric) == 1

    stop_arbiter(arbiter, pids, str(control_dir))

# ################################################################################################################################
# ################################################################################################################################
