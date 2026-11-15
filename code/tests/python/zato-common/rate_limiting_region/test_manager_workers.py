# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from multiprocessing import get_context

# Zato
from zato.common.rate_limiting.manager import RateLimitingManager
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.context import ForkProcess
    from zato.common.typing_ import callable_, list_, strdictlist

    callable_ = callable_
    ForkProcess = ForkProcess
    strdictlist = strdictlist

    processlist = list_[ForkProcess]

# ################################################################################################################################
# ################################################################################################################################

# Workers are forked, as the arbiter forks them, so that they inherit the mapping
_context = get_context('fork')

_slot_count = 4

# The metric that counts the requests refused because the table is at capacity
_table_full_metric = 0

# The metric through which each worker reports its permitted requests, one metric per slot
_first_permitted_metric = 1

# The channel and the security definition of the tests, with the prefixes that the server builds for them
_channel_id = 1
_channel_prefix = f'rest{_channel_id}:'

_sec_def_id = 2
_sec_def_prefix = f'basic_auth{_sec_def_id}:'

# Two persons resolved out of tokens issued under one security definition
_person_suffixes = ['alice:', 'bob:']

_client_ip = '10.0.0.1'

# A clock reading that every request of a test shares, within one window of an hour
_now_us = 1_800_000_000_000_000

# The requests that each rule permits within the window
_limit = 5

# How long a test waits for a worker, in seconds
_report_timeout = 20

# ################################################################################################################################
# ################################################################################################################################

def _new_rule_dicts() -> 'strdictlist':
    out:'strdictlist' = [{
        'cidr_list': ['10.0.0.0/8'],
        'time_range': [{
            'is_all_day': True,
            'disabled': False,
            'disallowed': False,
            'rate': 1000,
            'burst': 1000,
            'limit': _limit,
            'limit_unit': 'hour',
        }]
    }]
    return out

# ################################################################################################################################

def _new_region() -> 'SharedRegion':
    config = {
        'slot_count': _slot_count,
        'wake_capacity': 8,
        'cell_capacity': 64,
        'queue_count': 1,
        'metric_count': _first_permitted_metric + _slot_count,
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

def _new_manager(region:'SharedRegion', slot:'int') -> 'RateLimitingManager':
    """ Returns the manager of the worker of a slot, with the rules of the channel and of the security definition.
    """
    out = RateLimitingManager()
    out.use_region(region, slot, _table_full_metric)

    rule_dicts = _new_rule_dicts()
    out.set_channel_config(_channel_id, rule_dicts)
    out.set_sec_def_config(_sec_def_id, rule_dicts)

    return out

# ################################################################################################################################

def _is_channel_request_permitted(manager:'RateLimitingManager') -> 'bool':
    result = manager.check(_channel_id, _client_ip, _now_us, _channel_prefix)
    assert result is not None

    out = result.is_allowed
    return out

# ################################################################################################################################

def _is_person_request_permitted(manager:'RateLimitingManager', suffix:'str') -> 'bool':
    result = manager.check_sec_def(_sec_def_id, _client_ip, _now_us, _sec_def_prefix, suffix)
    assert result is not None

    out = result.is_allowed
    return out

# ################################################################################################################################

def _run_in_workers(region:'SharedRegion', target:'callable_', slots:'list_[int]') -> 'None':
    """ Forks a worker for each slot, runs the target in each of them at once and waits until each one exits.
    """
    processes:'processlist' = []

    for slot in slots:
        process = _context.Process(target=target, args=(region, slot))
        process.start()
        processes.append(process)

    for process in processes:
        process.join(_report_timeout)
        assert process.exitcode == 0

# ################################################################################################################################
# ################################################################################################################################

def _send_channel_requests(region:'SharedRegion', slot:'int') -> 'None':
    """ Sends the limit of the rule through the worker of a slot and reports how many requests were permitted.
    """
    manager = _new_manager(region, slot)

    for _ in range(_limit):
        if _is_channel_request_permitted(manager):
            region.metric_add(slot, _first_permitted_metric + slot, 1)

# ################################################################################################################################

def _clear_channel_counters(region:'SharedRegion', slot:'int') -> 'None':
    """ Clears the counters of the rule as zato.http-soap.rate-limiting.clear-counters does in the worker of a slot.
    """
    manager = _new_manager(region, slot)
    manager.clear_rule_counters(_channel_id, 0, _channel_prefix)

# ################################################################################################################################

def _clear_sec_def_counters(region:'SharedRegion', slot:'int') -> 'None':
    """ Clears the counters of the rule as zato.security.rate-limiting.clear-counters does in the worker of a slot.
    """
    manager = _new_manager(region, slot)
    manager.clear_sec_def_rule_counters(_sec_def_id, 0, _sec_def_prefix)

# ################################################################################################################################
# ################################################################################################################################

def test_the_limit_of_a_channel_is_shared_by_every_worker() -> 'None':
    region = _new_region()

    # Each worker receives as many requests as the rule permits in total ..
    slots = list(range(_slot_count))
    _run_in_workers(region, _send_channel_requests, slots)

    # .. and the rule permits its limit across all of them, not in each one.
    permitted = 0

    for slot in slots:
        permitted += region.metric_sum(_first_permitted_metric + slot)

    assert permitted == _limit

# ################################################################################################################################

def test_a_clear_of_channel_counters_through_one_worker_is_in_effect_in_another() -> 'None':
    region = _new_region()
    manager = _new_manager(region, 0)

    # This worker exhausts the limit ..
    for _ in range(_limit):
        assert _is_channel_request_permitted(manager)

    assert not _is_channel_request_permitted(manager)

    # .. another worker clears the counters of the rule ..
    _run_in_workers(region, _clear_channel_counters, [1])

    # .. and this worker permits the full limit again.
    for _ in range(_limit):
        assert _is_channel_request_permitted(manager)

    assert not _is_channel_request_permitted(manager)

# ################################################################################################################################

def test_a_clear_of_sec_def_counters_resets_the_counters_of_every_person() -> 'None':
    region = _new_region()
    manager = _new_manager(region, 0)

    # Each person has counters of their own and exhausts them ..
    for suffix in _person_suffixes:
        for _ in range(_limit):
            assert _is_person_request_permitted(manager, suffix)

        assert not _is_person_request_permitted(manager, suffix)

    # .. another worker clears the counters of the rule of the definition ..
    _run_in_workers(region, _clear_sec_def_counters, [1])

    # .. which resets the counters of each person, in this worker as well ..
    for suffix in _person_suffixes:
        assert _is_person_request_permitted(manager, suffix)

    # .. and leaves the counters of the channel rule, which share the address, as they were.
    for _ in range(_limit):
        assert _is_channel_request_permitted(manager)

    assert not _is_channel_request_permitted(manager)

# ################################################################################################################################
# ################################################################################################################################
