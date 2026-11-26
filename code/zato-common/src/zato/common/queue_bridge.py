# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

# The variable with the prefix of the stream keys of the queue bridge, which the queue bridge binary reads as well,
# so that environments sharing one Redis never read each other's streams
Stream_Prefix_Variable = 'Zato_Queue_Bridge_Stream_Prefix'

# The prefix of a standalone environment, which does not set the variable
Default_Stream_Prefix = 'zato:queue_bridge'

_stream_prefix = os.environ.get(Stream_Prefix_Variable)

if _stream_prefix is None:
    _stream_prefix = Default_Stream_Prefix

# ################################################################################################################################
# ################################################################################################################################

class QueueBridgeStreams:
    """ The Redis stream keys of the queue bridge in the environment of this process.
    """
    Prefix = _stream_prefix

    Command = f'{_stream_prefix}:stream:command'
    Reply   = f'{_stream_prefix}:stream:reply'
    Request = f'{_stream_prefix}:stream:request'

    # The prefix of a channel's recv stream, the channel's id follows
    Recv_Prefix = f'{_stream_prefix}:stream:recv:'

# ################################################################################################################################
# ################################################################################################################################
