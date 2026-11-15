# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from multiprocessing import get_context

# Zato
from zato.common.rate_limiting.common import Microseconds_Per_Second
from zato.common.rate_limiting.fixed_window import FixedWindowConfig, FixedWindowRegistry
from zato.common.rate_limiting.region import ModuleCtx as RegionCtx, RegionFixedWindowRegistry, RegionTokenBucketRegistry
from zato.common.rate_limiting.token_bucket import TokenBucketConfig, TokenBucketRegistry
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from multiprocessing.process import BaseProcess
    from pytest import LogCaptureFixture
    from zato.common.typing_ import any_, list_

    any_ = any_
    BaseProcess = BaseProcess
    Connection = Connection
    LogCaptureFixture = LogCaptureFixture

    connectionlist = list_[Connection]
    processlist    = list_[BaseProcess]

# ################################################################################################################################
# ################################################################################################################################

# Workers are forked, as the arbiter forks them, so that they inherit the mapping
_context = get_context('fork')

_slot_count = 4

# The metric that counts the requests refused because the table is at capacity
_table_full_metric = 0

# A key and its group, as SlottedCIDRMatcher.check builds them for the first time range of a rule
_key   = 'rest.orders:10.0.0.0/8:0'
_group = 'rest.orders:10.0.0.0/8:'

# A key of another rule
_other_key   = 'rest.orders:192.168.0.0/16:0'
_other_group = 'rest.orders:192.168.0.0/16:'

# A clock reading that every request of a test shares, so that no bucket refills during the test
_now_us = 1_800_000_000 * Microseconds_Per_Second

_requests_per_worker = 10

# How long a test waits for a worker to report, in seconds
_report_timeout = 20

# ################################################################################################################################
# ################################################################################################################################

def _new_region(cell_capacity:'int'=64) -> 'SharedRegion':
    config = {
        'slot_count': _slot_count,
        'wake_capacity': 8,
        'cell_capacity': cell_capacity,
        'queue_count': 1,
        'metric_count': 1,
        'series_capacity': 0,
        'series_key_bytes': 0,
        'dedup_capacity': 0,
        'breaker_capacity': 0,
        'lock_capacity': 0,
        'start_id': 1,
    }
    out = SharedRegion(config)
    return out

# ################################################################################################################################

def _count_allowed(region:'SharedRegion', slot:'int', conn:'Connection') -> 'None':
    """ Makes the requests of one worker against both kinds of counter and reports how many each one allowed.
    """
    token_buckets = RegionTokenBucketRegistry(region, slot, _table_full_metric)
    fixed_windows = RegionFixedWindowRegistry(region, slot, _table_full_metric)

    token_bucket_config = TokenBucketConfig.from_parts(1, 7)
    fixed_window_config = FixedWindowConfig.from_parts(5, 'hour')

    token_bucket_allowed = 0
    fixed_window_allowed = 0

    for _ in range(_requests_per_worker):
        if token_buckets.check_in_group(_key, _group, token_bucket_config, _now_us).is_allowed:
            token_bucket_allowed += 1

        if fixed_windows.check_in_group(_key, _group, fixed_window_config, _now_us).is_allowed:
            fixed_window_allowed += 1

    conn.send((token_bucket_allowed, fixed_window_allowed))

# ################################################################################################################################

def _clear_group(region:'SharedRegion', slot:'int', conn:'Connection') -> 'None':
    """ Clears the counters of one rule, as clear_rule_counters does in the worker that receives the request.
    """
    fixed_windows = RegionFixedWindowRegistry(region, slot, _table_full_metric)
    fixed_windows.remove_by_prefix(_group)
    conn.send('cleared')

# ################################################################################################################################

def _run_in_worker(region:'SharedRegion', slot:'int', target:'any_') -> 'any_':
    parent_conn, child_conn = _context.Pipe()

    process = _context.Process(target=target, args=(region, slot, child_conn))
    process.start()

    assert parent_conn.poll(_report_timeout)
    out = parent_conn.recv()

    process.join(_report_timeout)
    assert process.exitcode == 0

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_requests_spread_over_every_worker_are_limited_in_total() -> 'None':
    region = _new_region()

    # Every worker makes its requests at once ..
    connections:'connectionlist' = []
    processes:'processlist' = []

    for slot in range(_slot_count):
        parent_conn, child_conn = _context.Pipe()
        process = _context.Process(target=_count_allowed, args=(region, slot, child_conn))
        process.start()

        connections.append(parent_conn)
        processes.append(process)

    token_bucket_total = 0
    fixed_window_total = 0

    for parent_conn in connections:
        assert parent_conn.poll(_report_timeout)
        token_bucket_allowed, fixed_window_allowed = parent_conn.recv()

        token_bucket_total += token_bucket_allowed
        fixed_window_total += fixed_window_allowed

    for process in processes:
        process.join(_report_timeout)
        assert process.exitcode == 0

    # .. and together they are allowed the burst of the bucket and the limit of the window, not one per worker.
    assert token_bucket_total == 7
    assert fixed_window_total == 5

# ################################################################################################################################

def test_a_clear_through_one_worker_is_in_effect_in_every_worker() -> 'None':
    region = _new_region()

    token_buckets = RegionTokenBucketRegistry(region, 0, _table_full_metric)
    fixed_windows = RegionFixedWindowRegistry(region, 0, _table_full_metric)

    token_bucket_config = TokenBucketConfig.from_parts(1, 1)
    fixed_window_config = FixedWindowConfig.from_parts(1, 'hour')

    # Both rules spend their limits in this worker ..
    for key, group in ((_key, _group), (_other_key, _other_group)):
        assert token_buckets.check_in_group(key, group, token_bucket_config, _now_us).is_allowed
        assert not token_buckets.check_in_group(key, group, token_bucket_config, _now_us).is_allowed

        assert fixed_windows.check_in_group(key, group, fixed_window_config, _now_us).is_allowed
        assert not fixed_windows.check_in_group(key, group, fixed_window_config, _now_us).is_allowed

    # .. another worker clears the counters of one rule ..
    assert _run_in_worker(region, 1, _clear_group) == 'cleared'

    # .. which resets both kinds of counter of that rule ..
    assert token_buckets.check_in_group(_key, _group, token_bucket_config, _now_us).is_allowed
    assert fixed_windows.check_in_group(_key, _group, fixed_window_config, _now_us).is_allowed

    # .. and leaves the other rule as it was.
    assert not token_buckets.check_in_group(_other_key, _other_group, token_bucket_config, _now_us).is_allowed
    assert not fixed_windows.check_in_group(_other_key, _other_group, fixed_window_config, _now_us).is_allowed

# ################################################################################################################################

def test_a_new_key_is_refused_when_the_table_is_at_capacity(caplog:'LogCaptureFixture') -> 'None':

    # The token bucket and the fixed window of one key take both cells of the table ..
    region = _new_region(cell_capacity=2)

    token_buckets = RegionTokenBucketRegistry(region, 2, _table_full_metric)
    fixed_windows = RegionFixedWindowRegistry(region, 2, _table_full_metric)

    token_bucket_config = TokenBucketConfig.from_parts(1, 10)
    fixed_window_config = FixedWindowConfig.from_parts(10, 'hour')

    assert token_buckets.check_in_group(_key, _group, token_bucket_config, _now_us).is_allowed
    assert fixed_windows.check_in_group(_key, _group, fixed_window_config, _now_us).is_allowed

    # .. so a request for another key is refused, with an error logged and the metric increased ..
    with caplog.at_level(logging.ERROR):
        token_bucket_result = token_buckets.check_in_group(_other_key, _other_group, token_bucket_config, _now_us)
        fixed_window_result = fixed_windows.check_in_group(_other_key, _other_group, fixed_window_config, _now_us)

    assert not token_bucket_result.is_allowed
    assert token_bucket_result.retry_after_us == RegionCtx.Table_Full_Retry_After_us

    assert not fixed_window_result.is_allowed
    assert fixed_window_result.retry_after_us == RegionCtx.Table_Full_Retry_After_us

    assert region.metric_sum(_table_full_metric) == 2
    assert caplog.text.count(_other_key) == 2

    # .. while the key that has its cells is still served.
    assert token_buckets.check_in_group(_key, _group, token_bucket_config, _now_us).is_allowed

# ################################################################################################################################

def test_the_region_registries_decide_as_the_registries_of_one_process() -> 'None':
    region = _new_region()

    region_token_buckets = RegionTokenBucketRegistry(region, 0, _table_full_metric)
    region_fixed_windows = RegionFixedWindowRegistry(region, 0, _table_full_metric)

    local_token_buckets = TokenBucketRegistry()
    local_fixed_windows = FixedWindowRegistry()

    token_bucket_config = TokenBucketConfig.from_parts(2, 3)
    fixed_window_config = FixedWindowConfig.from_parts(4, 'second')

    # Requests arrive in bursts and pauses, across the end of several windows ..
    offsets_us = [0, 1, 2, 3, 4, 250_000, 500_000, 500_001, 999_999, 1_000_000, 1_000_001, 1_000_002, 1_000_003,
        1_000_004, 2_600_000, 2_600_001, 2_600_002, 2_600_003, 2_600_004]

    # .. and each one is allowed or refused by both pairs of registries alike.
    for offset_us in offsets_us:
        now_us = _now_us + offset_us

        region_token_bucket = region_token_buckets.check_in_group(_key, _group, token_bucket_config, now_us)
        local_token_bucket = local_token_buckets.check_inner(_key, token_bucket_config, now_us)

        region_fixed_window = region_fixed_windows.check_in_group(_key, _group, fixed_window_config, now_us)
        local_fixed_window = local_fixed_windows.check_inner(_key, fixed_window_config, now_us)

        assert (offset_us, region_token_bucket.is_allowed) == (offset_us, local_token_bucket.is_allowed)
        assert (offset_us, region_fixed_window.is_allowed) == (offset_us, local_fixed_window.is_allowed)
        assert (offset_us, region_fixed_window.remaining) == (offset_us, local_fixed_window.remaining)

# ################################################################################################################################
# ################################################################################################################################
