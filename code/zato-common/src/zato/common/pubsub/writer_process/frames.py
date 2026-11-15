# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The frames of the stream between a worker and the pub/sub writer process. Each frame is a four-byte length
# in network byte order followed by that many bytes of JSON. A worker sends one frame per item, with the kind
# of the item, an identifier unique within the worker, the instant of CLOCK_MONOTONIC at which its caller stops waiting
# and the body, and the writer sends one frame per reply, with the identifier of the item and either the body
# of the reply or the type and text of an error.

# stdlib
from json import dumps, loads
from struct import pack, unpack_from

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, list_

    any_ = any_
    anydict = anydict

    dictlist = list_['anydict']

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The length that precedes each frame, an unsigned 32-bit integer in network byte order
    Length_Format = '!I'
    Length_Size = 4

# ################################################################################################################################
# ################################################################################################################################

class ItemKind:
    Publish = 'publish'
    Ack     = 'ack'
    Lease   = 'lease'

# ################################################################################################################################
# ################################################################################################################################

class WriterItemError(Exception):
    """ The writer process could not write an item, with the type and the text of the error it raised.
    """
    def __init__(self, error_type:'str', error:'str') -> 'None':
        super().__init__(f'{error_type}: {error}')
        self.error_type = error_type
        self.error = error

class WriterItemExpired(Exception):
    """ The caller of an item stopped waiting before the writer ran it, so the writer does not run it.
    """

# ################################################################################################################################
# ################################################################################################################################

def encode(message:'anydict') -> 'bytes':
    body = dumps(message).encode('utf8')
    length = pack(ModuleCtx.Length_Format, len(body))

    out = length + body
    return out

# ################################################################################################################################

def new_item(kind:'str', item_id:'int', expires_at:'float', body:'any_') -> 'bytes':
    message = {
        'kind': kind,
        'item_id': item_id,
        'expires_at': expires_at,
        'body': body,
    }
    out = encode(message)
    return out

# ################################################################################################################################

def new_reply(item_id:'int', body:'any_') -> 'bytes':
    message = {
        'item_id': item_id,
        'body': body,
    }
    out = encode(message)
    return out

# ################################################################################################################################

def new_error_reply(item_id:'int', error:'Exception') -> 'bytes':
    message = {
        'item_id': item_id,
        'error_type': type(error).__name__,
        'error': str(error),
    }
    out = encode(message)
    return out

# ################################################################################################################################
# ################################################################################################################################

class FrameReader:
    """ Collects the bytes of a stream and returns each frame once all of its bytes arrived.
    """

    def __init__(self) -> 'None':
        self.buffer = bytearray()

    def feed(self, data:'bytes') -> 'dictlist':
        """ Adds the bytes of one read and returns the messages of the frames that are now complete, in their order.
        """
        self.buffer.extend(data)
        out:'dictlist' = []

        while len(self.buffer) >= ModuleCtx.Length_Size:
            length, = unpack_from(ModuleCtx.Length_Format, self.buffer)
            end = ModuleCtx.Length_Size + length

            # The rest of the frame is still to arrive
            if len(self.buffer) < end:
                break

            body = bytes(self.buffer[ModuleCtx.Length_Size:end])
            del self.buffer[:end]

            message = loads(body)
            out.append(message)

        return out

# ################################################################################################################################
# ################################################################################################################################
