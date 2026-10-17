# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The counting service of the channel suites with the get_queue_response hook defined - what a redeploy replaces the
# module without the hook with, to show that the very next request goes through the hook.

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

# What the hook puts in front of the message id it answers with
_hook_response_prefix = 'hooked:'

# ################################################################################################################################
# ################################################################################################################################

class Counting(Service):
    """ Counts its instantiations and answers a queued request with the id of its message.
    """

    name = 'test.queue-delivery.channel.counting'

    def __init__(self) -> 'None':
        super().__init__()
        _instances.append(1)

    def handle(self) -> 'None':
        pass

    def get_queue_response(self) -> 'None':
        self.response.payload = _hook_response_prefix + self.request.queue.msg_id

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
