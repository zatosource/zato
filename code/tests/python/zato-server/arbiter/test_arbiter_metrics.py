# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from arbiter_common import get_pids, Region_Config, Requests_Channel, Requests_Counter, Slot_Count, start_arbiter, \
    stop_arbiter
from zato.server.metrics_region import ModuleCtx
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

def test_every_worker_records_its_metrics_into_the_row_of_its_slot(tmp_path:'Path') -> 'None':
    control_dir = tmp_path / 'control'
    control_dir.mkdir()

    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'record_metric', str(control_dir))
    pids = get_pids(region)

    # The series of the counter is registered once, whichever worker registered it first ..
    key = ModuleCtx.Key_Separator.join((Requests_Counter.name, Requests_Channel))
    indexes = [index for series_key, _kind, index in region.series_list() if series_key == key]

    assert len(indexes) == 1

    # .. and each worker added its own count in the row of its own slot.
    index = indexes[0]

    for slot in range(Slot_Count):
        assert region.series_value(slot, index) == slot + 1

    stop_arbiter(arbiter, pids, str(control_dir))

# ################################################################################################################################
# ################################################################################################################################
