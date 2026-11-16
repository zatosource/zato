# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The service that the scaling measurement deploys through the pickup directory of the server.

# Zato
from zato.common.worker_slot import get_slot_or_single
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class CPUBound(Service):
    """ Performs a fixed amount of interpreter work and returns the slot of the worker that performed it.
    """
    name = 'test.multi-cpu.perf.cpu-bound'

    # The number of iterations of the arithmetic loop, which takes about one millisecond of CPU time
    Iterations = 20_000

    def handle(self) -> 'None':
        total = 0

        for index in range(self.Iterations):
            total += index * index % 7

        self.response.payload = {
            'slot': get_slot_or_single(),
            'total': total,
        }

# ################################################################################################################################
# ################################################################################################################################
