# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from arbiter_common import CPU_Byte_Bits, Events_Metric, get_pids, Query_Metric, Region_Config, Slot_Count, start_arbiter, \
    stop_arbiter, Writes_Metric
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.context import ForkProcess
    from pathlib import Path
    from zato.common.typing_ import intlist

    ForkProcess = ForkProcess
    intlist = intlist
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The period of the synthetic quotas, in microseconds
    Period = 100_000

# ################################################################################################################################
# ################################################################################################################################

def _write_cpu_max(tmp_path:'Path', contents:'str') -> 'str':

    # The file is kept outside of the tmp directory of the arbiter, which the arbiter leaves empty on stop
    cgroup_dir = tmp_path / 'cgroup'
    cgroup_dir.mkdir()

    path = cgroup_dir / 'cpu.max'
    _ = path.write_text(contents)

    out = str(path)
    return out

# ################################################################################################################################

def _start_on_slot_count_cpus(region:'SharedRegion', tmp_dir:'str', cpu_max_path:'str', cpus:'intlist') -> 'ForkProcess':

    # The arbiter inherits an affinity set of as many CPUs as there are slots, after which the test process
    # returns to its own affinity set
    own_cpus = os.sched_getaffinity(0)
    os.sched_setaffinity(0, cpus)

    out = start_arbiter(region, 'report_cpus', tmp_dir, None, cpu_max_path)
    os.sched_setaffinity(0, own_cpus)

    return out

# ################################################################################################################################

def _get_slot_count_cpus() -> 'intlist':
    cpus = sorted(os.sched_getaffinity(0))

    out = cpus[:Slot_Count]
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_every_worker_inherits_the_frozen_objects(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)

    arbiter = start_arbiter(region, 'report_cpus', tmp_dir)
    assert region.metric_sum(Writes_Metric) == Slot_Count

    pids = get_pids(region)
    stop_arbiter(arbiter, pids, tmp_dir)

# ################################################################################################################################

def test_as_many_workers_as_cpus_run_each_on_the_cpu_of_its_slot(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path / 'tmp')
    os.mkdir(tmp_dir)

    cpus = _get_slot_count_cpus()
    cpu_max_path = _write_cpu_max(tmp_path, f'max {ModuleCtx.Period}\n')

    region = SharedRegion(Region_Config)
    arbiter = _start_on_slot_count_cpus(region, tmp_dir, cpu_max_path, cpus)

    # Each worker may run on one CPU only ..
    assert region.metric_sum(Events_Metric) == Slot_Count

    # .. and that CPU is the one at the position of its slot.
    expected = 0

    for slot, cpu in enumerate(cpus):
        expected += (cpu + 1) << (CPU_Byte_Bits * slot)

    assert region.metric_sum(Query_Metric) == expected

    pids = get_pids(region)
    stop_arbiter(arbiter, pids, tmp_dir)

# ################################################################################################################################

def test_no_worker_is_pinned_under_a_quota_smaller_than_its_cpus(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path / 'tmp')
    os.mkdir(tmp_dir)

    cpus = _get_slot_count_cpus()
    quota = (Slot_Count - 1) * ModuleCtx.Period
    cpu_max_path = _write_cpu_max(tmp_path, f'{quota} {ModuleCtx.Period}\n')

    region = SharedRegion(Region_Config)
    arbiter = _start_on_slot_count_cpus(region, tmp_dir, cpu_max_path, cpus)

    # Each worker may run on every CPU of the affinity set that the arbiter inherited
    assert region.metric_sum(Events_Metric) == Slot_Count * Slot_Count
    assert region.metric_sum(Query_Metric) == 0

    pids = get_pids(region)
    stop_arbiter(arbiter, pids, tmp_dir)

# ################################################################################################################################
# ################################################################################################################################
