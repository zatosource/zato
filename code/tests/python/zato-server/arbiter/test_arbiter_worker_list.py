# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import sys
from multiprocessing import get_context

# Zato
from arbiter_common import get_pids, new_config, Region_Config, Slot_Count, stop_arbiter, Tested_Slot, wait_until, \
    WorkerUnderTest
from zato.common.pubsub.ownership import is_owner
from zato.server.arbiter import Arbiter
from zato.server.control.hub import EntryStatus
from zato.server.control.queries import QueryName, QueryRouter
from zato.server.worker_list import answer_worker_list, bind_worker_list, get_worker_list
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anylist, strlist
    from zato.server.arbiter_config import WorkerContext

    any_ = any_
    anylist = anylist
    Path = Path
    strlist = strlist
    WorkerContext = WorkerContext

# ################################################################################################################################
# ################################################################################################################################

_context = get_context('fork')

# The subscription keys that every worker of the test knows
_sub_key_count = 30
_sub_keys = [f'zpsk.test.worker-list.{index}' for index in range(_sub_key_count)]

# The file into which the tested slot writes the worker list
_result_name = 'worker-list.json'

# ################################################################################################################################
# ################################################################################################################################

class _ListWorker(WorkerUnderTest):
    """ A worker of the test that answers each query through the query router of the server.
    """
    def __init__(self, region:'SharedRegion', ctx:'WorkerContext') -> 'None':
        self.router = QueryRouter()
        self.router.register(QueryName.Worker_Get_List, answer_worker_list)

        super().__init__(region, ctx, True)

    def on_query(self, body:'any_') -> 'any_':
        out = self.router.on_query(body)
        return out

# ################################################################################################################################

def _get_sub_keys() -> 'strlist':
    return _sub_keys

# ################################################################################################################################

def _write_result(result_path:'str', rows:'anylist') -> 'None':
    """ Writes the worker list to a file that the test reads only once it is complete.
    """
    partial_path = result_path + '.partial'

    with open(partial_path, 'w') as result_file:
        json.dump(rows, result_file)

    os.rename(partial_path, result_path)

# ################################################################################################################################

def _run_arbiter(region:'SharedRegion', tmp_dir:'str', result_path:'str') -> 'None':

    def worker_main(ctx:'WorkerContext') -> 'None':
        worker = _ListWorker(region, ctx)
        bind_worker_list(region, ctx.slot, ctx.generation, worker.client.query, _get_sub_keys)
        worker.report_ready()

        # The tested slot serves the worker list once every slot is ready
        if ctx.slot == Tested_Slot:
            worker.wait_for_all_ready()
            rows = get_worker_list()
            _write_result(result_path, rows)

        worker.serve()

    config = new_config(tmp_dir)

    arbiter = Arbiter(region, worker_main, config)
    exit_code = arbiter.run()

    sys.exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################

def test_the_worker_list_describes_every_slot(tmp_path:'Path') -> 'None':
    region = SharedRegion(Region_Config)

    tmp_dir = tmp_path / 'tmp'
    tmp_dir.mkdir()

    result_path = str(tmp_path / _result_name)

    arbiter = _context.Process(target=_run_arbiter, args=(region, str(tmp_dir), result_path))
    arbiter.start()

    try:
        assert wait_until(os.path.exists, (result_path,))

        pids = get_pids(region)
        stop_arbiter(arbiter, pids, str(tmp_dir))

    finally:
        if arbiter.is_alive():
            arbiter.kill()

    with open(result_path) as result_file:
        rows = json.load(result_file)

    heartbeat_threshold_ms = new_config(str(tmp_dir)).heartbeat_threshold * 1000

    # Every slot answered with the process and the generation that the region recorded for it ..
    assert [row['slot'] for row in rows] == list(range(Slot_Count))

    for row in rows:
        slot = row['slot']

        assert row['response'] == EntryStatus.OK
        assert row['pid'] == pids[slot]
        assert row['generation'] == region.slot_generation(slot)
        assert row['state'] == 'ready'
        assert 0 <= row['heartbeat_age_ms'] < heartbeat_threshold_ms

        # .. each slot counts the keys that it owns ..
        owned = [sub_key for sub_key in _sub_keys if is_owner(sub_key, slot, Slot_Count)]
        assert row['sub_key_count'] == len(owned)

    # .. so the counts add up to every key, and only the first slot runs the singleton duties.
    assert sum(row['sub_key_count'] for row in rows) == _sub_key_count
    assert [row['is_singleton_owner'] for row in rows] == [True, False, False]

# ################################################################################################################################
# ################################################################################################################################
