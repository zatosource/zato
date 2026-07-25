# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The runtime side of AS4, spread over one module per concern.

- routing - what an accepted payload and a delivered signal are handed over as
- outconn - one outgoing connection: send, send_to, pull and ping
- channel - one channel: the inbound pipeline, duplicate detection and routing
"""

# Zato
from zato.server.connection.as4.channel import AS4ChannelRuntime
from zato.server.connection.as4.outconn import AS4Wrapper
from zato.server.connection.as4.routing import build_routed_message, build_routed_signal

# ################################################################################################################################
# ################################################################################################################################

__all__ = (
    'build_routed_message',
    'build_routed_signal',
    'AS4ChannelRuntime',
    'AS4Wrapper',
)

# ################################################################################################################################
# ################################################################################################################################
