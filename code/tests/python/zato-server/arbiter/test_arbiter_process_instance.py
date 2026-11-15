# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from arbiter_common import get_pids, Region_Config, Slot_Count, start_arbiter, stop_arbiter, Writes_Metric
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

def test_every_worker_has_the_process_instance_of_its_slot(tmp_path:'Path') -> 'None':
    control_dir = tmp_path / 'control'
    control_dir.mkdir()

    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'report_process_instance', str(control_dir))
    pids = get_pids(region)

    # Every worker reported ready after its check, and each found the instance of its own slot
    assert region.metric_sum(Writes_Metric) == Slot_Count

    stop_arbiter(arbiter, pids, str(control_dir))

# ################################################################################################################################

def test_the_log_records_of_every_worker_name_its_slot(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)

    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'report_log_slot', tmp_dir)
    pids = get_pids(region)

    assert region.metric_sum(Writes_Metric) == Slot_Count

    stop_arbiter(arbiter, pids, tmp_dir)

# ################################################################################################################################
# ################################################################################################################################
