# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from live_windows.guest_versions import item_versions
from live_windows.settings import Shards, Versions
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _pytest.python import Function
    from pytest import Item

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The duration of each test on one guest, in seconds, by which the tests of each version are divided among its shards
    Weights = {
        'test_ping':                                 1.0,
        'test_schedules_listed':                     1.0,
        'test_audit_log_records_pickup':             9.0,
        'test_ping_fails_with_wrong_password':       2.0,
        'test_agent_responds':                       1.5,
        'test_exchange_account_reaches_every_share': 1.1,
        'test_round_trip':                           1.1,
        'test_control_share_refused':                4.0,
        'test_single_file':                          5.5,
        'test_burst':                                9.0,
        'test_fan_out':                              8.0,
        'test_empty_file_rejected':                  6.0,
        'test_temp_then_rename':                     6.0,
        'test_slow_writer':                          9.0,
        'test_locked_file':                          9.0,
        'test_archive_and_partner_drop':             7.0,
        'test_partner_on_other_guest':              10.0,
        'test_labels_per_site':                      9.0,
        'test_daily_extract':                        7.0,
        'test_both_directions':                     10.0,
        'test_claim_contention':                    15.0,
        'test_smb_service_restart':                 15.0,
        'test_port_blocked':                        18.0,
        'test_guest_paused':                        18.0,
        'test_credential_rotation':                 15.0,
        'test_share_removed':                       13.0,
        'test_server_restart':                      13.0,
        'test_switchover':                          15.0,
    }

    # How long a shard takes to create the definitions of one more guest through the Dashboard, in seconds
    Guest_Setup_Weight = 10.0

# ################################################################################################################################
# ################################################################################################################################

itemlist = list['Item']
shardkey = tuple[str, int]

# ################################################################################################################################
# ################################################################################################################################

def _weight(item:'Item') -> 'float':
    function:'Function' = cast_('Function', item)

    out = ModuleCtx.Weights[function.originalname]
    return out

# ################################################################################################################################

def current_shard() -> 'tuple[int, int]':
    """ Returns the index of the shard of this process and the number of shards.
    """
    value = os.environ[Shards.Variable]
    index_text, count_text = value.split(Shards.Separator)

    index = int(index_text)
    count = int(count_text)

    version_count = len(Versions.All)

    if count % version_count:
        raise Exception(f'The number of shards {count} is not a multiple of the number of versions {version_count}')

    if index >= count:
        raise Exception(f'The index of the shard {index} is not lower than the number of shards {count}')

    out = index, count
    return out

# ################################################################################################################################

def is_sharded() -> 'bool':
    out = Shards.Variable in os.environ
    return out

# ################################################################################################################################

def shard_items(items:'itemlist', index:'int', count:'int') -> 'itemlist':
    """ Returns the tests of one shard, in the order of their collection. Each version has the same number of shards.
    A test that runs against two guests belongs to the first shard of the first of its versions, which also creates
    the definitions of the second guest, and the other tests of each version go to the shard of that version
    that has the least work so far, the longest test first.
    """
    version_count = len(Versions.All)
    shards_per_version = count // version_count

    own_version = Versions.All[index % version_count]
    own_shard:'shardkey' = own_version, index // version_count

    loads:'dict[shardkey, float]' = {}
    for version in Versions.All:
        for version_shard in range(shards_per_version):
            loads[version, version_shard] = 0.0

    assignment:'dict[str, shardkey]' = {}
    single_guest:'dict[str, itemlist]' = {}
    extra_guests:'set[tuple[shardkey, str]]' = set()

    for version in Versions.All:
        single_guest[version] = []

    # The tests that run against two guests are placed first, each other guest of a shard adding to its work ..
    for item in items:

        versions = item_versions(item)
        first_version = versions[0]

        if len(versions) > 1:
            key:'shardkey' = first_version, 0
            assignment[item.nodeid] = key
            loads[key] += _weight(item)

            for other_version in versions[1:]:
                extra_guest = key, other_version
                if extra_guest not in extra_guests:
                    extra_guests.add(extra_guest)
                    loads[key] += ModuleCtx.Guest_Setup_Weight
        else:
            single_guest[first_version].append(item)

    # .. then each of the other ones goes to the shard of its version with the least work so far ..
    for version, version_items in single_guest.items():

        by_weight = sorted(version_items, key=_weight, reverse=True)

        for item in by_weight:

            lightest:'shardkey' = version, 0

            for version_shard in range(1, shards_per_version):
                candidate:'shardkey' = version, version_shard
                if loads[candidate] < loads[lightest]:
                    lightest = candidate

            assignment[item.nodeid] = lightest
            loads[lightest] += _weight(item)

    # .. and the shard keeps its own tests in the order in which they were collected.
    out:'itemlist' = []

    for item in items:
        if assignment[item.nodeid] == own_shard:
            out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################
