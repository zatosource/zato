# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Helpers for tests that run the pub/sub backend and push delivery in the test process itself.

# Zato
from zato.common.pubsub.fence import DeliveryFence
from zato.server.server_region import new_server_region

# ################################################################################################################################
# ################################################################################################################################

def _on_fenced() -> 'None':
    raise AssertionError('The only slot of the test process received no replacement')

# ################################################################################################################################

def new_single_slot_fence() -> 'DeliveryFence':
    """ Returns the fence of the only worker of a region with one slot, which owns every subscription key.
    """
    region = new_server_region(1, 0)
    generation = region.next_slot_generation(0)

    out = DeliveryFence(region, 0, generation, _on_fenced)
    return out

# ################################################################################################################################
# ################################################################################################################################
