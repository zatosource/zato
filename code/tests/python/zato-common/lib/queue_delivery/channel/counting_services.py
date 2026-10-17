# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The counting service of the channel suites - it counts its own instantiations and has no get_queue_response hook,
# so a channel with the queue on never instantiates it on the way in. A redeploy replaces this module with the one
# that defines the hook and then puts this one back.

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

# Every instantiation since the counter was last cleared
_instances:'anylist' = []

# ################################################################################################################################
# ################################################################################################################################

class Counting(Service):
    """ Counts its instantiations and does nothing else.
    """

    name = 'test.queue-delivery.channel.counting'

    def __init__(self) -> 'None':
        super().__init__()
        _instances.append(1)

    def handle(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class GetCounting(Service):
    """ How many times the counting service was instantiated since the counter was last cleared.
    """

    name = 'test.queue-delivery.channel.get-counting'

    def handle(self) -> 'None':
        self.response.payload = {'count': len(_instances)}

# ################################################################################################################################
# ################################################################################################################################

class ClearCounting(Service):
    """ Forgets every instantiation counted so far.
    """

    name = 'test.queue-delivery.channel.clear-counting'

    def handle(self) -> 'None':
        _instances.clear()
        self.response.payload = {'count': 0}

# ################################################################################################################################
# ################################################################################################################################
