# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys
from json import loads

# Zato
from zato.common.pubsub import ownership
from zato.common.pubsub.ownership import get_owner_slot, is_owner

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, strlist

    intlist = intlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The number of worker slots of the tests
    Slot_Count = 8

    # How many subscription keys the distribution tests assign
    Key_Count = 100_000

    # How far the share of one slot may depart from an even share, as a fraction of it
    Share_Tolerance = 0.05

    # How many subscription keys the processes of the stability test assign
    Process_Key_Count = 200

    # The hash seeds of the processes of the stability test
    Hash_Seeds = ['1', '2', '3']

    # Assigns the keys in a separate interpreter and prints their owners as JSON
    Process_Code = """
import sys
from importlib.util import module_from_spec, spec_from_file_location
from json import dumps

spec = spec_from_file_location('ownership', sys.argv[1])
module = module_from_spec(spec)
spec.loader.exec_module(module)

owners = []

for index in range(int(sys.argv[2])):
    owners.append(module.get_owner_slot(f'zpsk.rest.{index}', int(sys.argv[3])))

print(dumps(owners))
"""

# ################################################################################################################################
# ################################################################################################################################

def _new_sub_keys(count:'int') -> 'strlist':
    out:'strlist' = []

    for index in range(count):
        out.append(f'zpsk.rest.{index}')

    return out

# ################################################################################################################################

def _get_owners(sub_keys:'strlist', slot_count:'int') -> 'intlist':
    out:'intlist' = []

    for sub_key in sub_keys:
        owner = get_owner_slot(sub_key, slot_count)
        out.append(owner)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_exactly_one_slot_owns_each_key() -> 'None':
    sub_keys = _new_sub_keys(ModuleCtx.Process_Key_Count)

    for sub_key in sub_keys:
        owner = get_owner_slot(sub_key, ModuleCtx.Slot_Count)
        owners:'intlist' = []

        for slot in range(ModuleCtx.Slot_Count):
            if is_owner(sub_key, slot, ModuleCtx.Slot_Count):
                owners.append(slot)

        assert owners == [owner]

    # A server of one worker owns every key in its only slot
    assert _get_owners(sub_keys, 1) == [0] * ModuleCtx.Process_Key_Count

# ################################################################################################################################

def test_every_process_selects_the_same_owner() -> 'None':
    sub_keys = _new_sub_keys(ModuleCtx.Process_Key_Count)
    expected = _get_owners(sub_keys, ModuleCtx.Slot_Count)

    # Each worker is a separate process with a hash seed of its own ..
    for hash_seed in ModuleCtx.Hash_Seeds:
        env = dict(os.environ)
        env['PYTHONHASHSEED'] = hash_seed

        args = [sys.executable, '-c', ModuleCtx.Process_Code, ownership.__file__,
            str(ModuleCtx.Process_Key_Count), str(ModuleCtx.Slot_Count)]

        result = subprocess.run(args, env=env, capture_output=True, text=True, check=True)

        # .. and it selects the owners that this process selects.
        assert loads(result.stdout) == expected

# ################################################################################################################################

def test_each_slot_owns_an_even_share_of_the_keys() -> 'None':
    sub_keys = _new_sub_keys(ModuleCtx.Key_Count)
    owners = _get_owners(sub_keys, ModuleCtx.Slot_Count)

    even_share = ModuleCtx.Key_Count / ModuleCtx.Slot_Count
    tolerance = even_share * ModuleCtx.Share_Tolerance

    for slot in range(ModuleCtx.Slot_Count):
        share = owners.count(slot)
        assert abs(share - even_share) <= tolerance

# ################################################################################################################################

def test_an_added_slot_takes_keys_only_for_itself() -> 'None':
    sub_keys = _new_sub_keys(ModuleCtx.Key_Count)

    added_slot = ModuleCtx.Slot_Count
    slot_count = ModuleCtx.Slot_Count + 1

    before = _get_owners(sub_keys, ModuleCtx.Slot_Count)
    after = _get_owners(sub_keys, slot_count)

    moved_count = 0

    # A key changes its owner only to the added slot ..
    for owner_before, owner_after in zip(before, after):
        if owner_before != owner_after:
            assert owner_after == added_slot
            moved_count += 1

    # .. which receives its share of the keys.
    even_share = ModuleCtx.Key_Count / slot_count
    tolerance = even_share * ModuleCtx.Share_Tolerance

    assert abs(moved_count - even_share) <= tolerance

# ################################################################################################################################

def test_a_removed_slot_releases_only_its_own_keys() -> 'None':
    sub_keys = _new_sub_keys(ModuleCtx.Key_Count)

    slot_count = ModuleCtx.Slot_Count - 1
    removed_slot = slot_count

    before = _get_owners(sub_keys, ModuleCtx.Slot_Count)
    after = _get_owners(sub_keys, slot_count)

    # A key changes its owner only when the removed slot owned it
    for owner_before, owner_after in zip(before, after):
        if owner_before == removed_slot:
            assert owner_after != removed_slot
        else:
            assert owner_after == owner_before

# ################################################################################################################################
# ################################################################################################################################
