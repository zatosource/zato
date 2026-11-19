# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from live_windows.settings import Partners, Shards, Versions
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _pytest.python import Function
    from pytest import Item
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The duration of each test on one guest, in seconds, measured in a session that ran the tests one after another,
    # by which the tests of each version are divided among its shards
    Weights = {
        'test_agent_responds':                       1.5,
        'test_exchange_account_reaches_every_share': 1.1,
        'test_round_trip':                           1.1,
        'test_control_share_refused':                4.0,
        'test_single_file':                          5.5,
        'test_burst':                               13.0,
        'test_fan_out':                              6.0,
        'test_empty_file_rejected':                  6.0,
        'test_temp_then_rename':                     6.0,
        'test_slow_writer':                          8.5,
        'test_locked_file':                          8.8,
        'test_archive_and_partner_drop':             6.8,
        'test_partner_on_other_guest':               6.3,
        'test_labels_per_site':                      8.0,
        'test_daily_extract':                        6.3,
        'test_both_directions':                      7.0,
        'test_claim_contention':                    10.0,
        'test_smb_service_restart':                 13.8,
        'test_port_blocked':                        17.5,
        'test_guest_paused':                        18.3,
        'test_credential_rotation':                 14.0,
        'test_share_removed':                       12.5,
        'test_server_restart':                      10.5,
        'test_switchover':                          15.0,
    }

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

def _in_version_order(versions:'strlist') -> 'strlist':
    out:'strlist' = []

    for version in Versions.All:
        if version in versions:
            out.append(version)

    return out

# ################################################################################################################################

def item_versions(item:'Item') -> 'strlist':
    """ Returns the versions of the guests that a test runs against, in the order of all the versions.
    """
    versions:'strlist' = []

    # A test without a version parameter names its guests ..
    if marker := item.get_closest_marker('guests'):
        versions.extend(marker.args)

    # .. and a test with one runs against the guest of its version, and against the partner guest if it needs one.
    else:
        function:'Function' = cast_('Function', item)
        version:'str' = cast_('str', function.callspec.params['version'])
        versions.append(version)

        if item.get_closest_marker('partner_guest'):
            partner_version = Partners[version]
            versions.append(partner_version)

    out = _in_version_order(versions)
    return out

# ################################################################################################################################

def needed_versions(items:'itemlist') -> 'strlist':
    """ Returns the versions of the guests that any of the tests runs against.
    """
    versions:'strlist' = []

    for item in items:
        versions.extend(item_versions(item))

    out = _in_version_order(versions)
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
    A test that runs against two guests belongs to the first shard of the first of its versions, and the other tests
    of each version go to the shard of that version that has the least work so far, the longest test first.
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

    for version in Versions.All:
        single_guest[version] = []

    # The tests that run against two guests are placed first ..
    for item in items:

        versions = item_versions(item)
        first_version = versions[0]

        if len(versions) > 1:
            key:'shardkey' = first_version, 0
            assignment[item.nodeid] = key
            loads[key] += _weight(item)
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
