# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import OrderedDict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strnone

# ################################################################################################################################
# ################################################################################################################################

# How many bytes of payloads the server keeps at most.
Max_Payload_Cache_Size = 64 * 1024 * 1024

# ################################################################################################################################
# ################################################################################################################################

class PayloadCache:
    """ The payloads of the messages that push delivery read most recently, up to a total size, by the identifier
    of each message. A message pushed to many subscribers is read from the database and decrypted once
    rather than once per subscriber. A payload changes only through an edit of its message, which removes it from here.
    """

    def __init__(self, max_size:'int') -> 'None':
        self.max_size = max_size
        self.size = 0
        self._payloads:'OrderedDict[str, tuple[str, int]]' = OrderedDict()

# ################################################################################################################################

    def get(self, msg_id:'str') -> 'strnone':
        """ Returns the payload of a message, or None if it is not kept.
        """
        entry = self._payloads.get(msg_id)

        if entry is None:
            return None

        self._payloads.move_to_end(msg_id)

        payload, _ = entry
        return payload

# ################################################################################################################################

    def put(self, msg_id:'str', payload:'str', size:'int') -> 'None':
        """ Keeps the payload of a message, dropping those used least recently once the total size is exceeded.
        """
        # A payload larger than the whole cache is not kept ..
        if size > self.max_size:
            return

        # .. and neither is one kept already, which another delivery read at the same time.
        if msg_id in self._payloads:
            return

        self._payloads[msg_id] = (payload, size)
        self.size += size

        while self.size > self.max_size:
            _, (_, evicted_size) = self._payloads.popitem(last=False)
            self.size -= evicted_size

# ################################################################################################################################

    def remove(self, msg_id:'str') -> 'None':
        """ Stops keeping the payload of a message, so that the next delivery reads it from the database.
        """
        entry = self._payloads.pop(msg_id, None)

        # A payload that is not kept has nothing to subtract
        if entry is None:
            return

        _, size = entry
        self.size -= size

# ################################################################################################################################
# ################################################################################################################################
