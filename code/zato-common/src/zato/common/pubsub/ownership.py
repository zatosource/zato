# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The slot that owns a subscription key, selected by rendezvous hashing of the key over the slot indices. Each slot
# receives a weight computed from the key and the slot index, and the slot with the highest weight owns the key.
# The weight depends on nothing but the key and the index, so every worker selects the same owner, the owner remains
# the same across respawns of its slot, and a change of the slot count moves only the keys that the added slots win
# or that the removed slots owned.

# stdlib
from hashlib import blake2b

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The size, in bytes, of the digest that forms the weight of a slot
    Digest_Size = 8

    # Separates the subscription key from the slot index in the input of the digest
    Separator = '\0'

# ################################################################################################################################
# ################################################################################################################################

def get_slot_weight(sub_key:'str', slot:'int') -> 'int':
    """ Returns the weight of one slot for one subscription key.
    """
    text = f'{sub_key}{ModuleCtx.Separator}{slot}'
    data = text.encode('utf8')

    digest = blake2b(data, digest_size=ModuleCtx.Digest_Size).digest()

    # The digest is read in the big-endian order, the default of int.from_bytes
    out = int.from_bytes(digest)
    return out

# ################################################################################################################################

def get_owner_slot(sub_key:'str', slot_count:'int') -> 'int':
    """ Returns the index of the slot that owns a subscription key.
    """
    out = 0
    best_weight = get_slot_weight(sub_key, 0)

    for slot in range(1, slot_count):
        weight = get_slot_weight(sub_key, slot)

        if weight > best_weight:
            best_weight = weight
            out = slot

    return out

# ################################################################################################################################

def is_owner(sub_key:'str', slot:'int', slot_count:'int') -> 'bool':
    """ Returns whether the worker of a slot owns a subscription key.
    """
    owner = get_owner_slot(sub_key, slot_count)

    out = owner == slot
    return out

# ################################################################################################################################
# ################################################################################################################################
