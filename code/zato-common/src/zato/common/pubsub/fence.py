# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The fence of a worker that runs delivery loops. It holds the slot of the worker and the generation of the slot under
# which the worker was started, and a worker whose slot received a replacement of a later generation sends no further
# attempt and records no further delivery outcome.

# Zato
from zato.common.pubsub.delivery import DeliveryFenced
from zato.common.pubsub.ownership import is_owner

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_
    from zato_ipc_core.zato_ipc_core import SharedRegion

    callable_ = callable_
    SharedRegion = SharedRegion

# ################################################################################################################################
# ################################################################################################################################

class DeliveryFence:
    """ The slot of a worker that runs delivery loops and the generation of the slot under which the worker was started.
    """
    def __init__(self, region:'SharedRegion', slot:'int', generation:'int', on_fenced:'callable_') -> 'None':
        self.region = region
        self.slot = slot
        self.generation = generation

        # Terminates the worker once a delivery loop found its generation superseded
        self.on_fenced = on_fenced

# ################################################################################################################################

    def owns(self, sub_key:'str') -> 'bool':
        """ Returns whether the worker owns a subscription key.
        """
        slot_count = self.region.slot_count

        out = is_owner(sub_key, self.slot, slot_count)
        return out

# ################################################################################################################################

    def check(self) -> 'None':
        """ Raises DeliveryFenced when a replacement worker started in the slot of this worker.
        """
        generation = self.region.slot_generation(self.slot)

        if generation != self.generation:
            raise DeliveryFenced(f'Slot {self.slot} has generation {generation}, the worker has {self.generation}')

# ################################################################################################################################
# ################################################################################################################################
