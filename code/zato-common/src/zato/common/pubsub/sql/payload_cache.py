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

class PayloadEpoch:
    """ The payload epoch of the server. Each edit of a message advances it.
    """

    def __init__(self) -> 'None':
        self.value = 0

    def get(self) -> 'int':
        return self.value

    def advance(self) -> 'None':
        self.value += 1

# ################################################################################################################################
# ################################################################################################################################

class PayloadCache:
    """ The payloads of the messages that push delivery read most recently, up to a total size, by the identifier
    of each message. A message pushed to many subscribers is read from the database and decrypted once
    rather than once per subscriber. A payload changes only through an edit of its message, which advances the payload
    epoch, after which the cache drops the payloads it keeps.
    """

    def __init__(self, max_size:'int', epoch:'PayloadEpoch') -> 'None':
        self.max_size = max_size
        self.size = 0
        self._payloads:'OrderedDict[str, tuple[str, int]]' = OrderedDict()

        # The payloads kept were read under this value of the epoch
        self.epoch = epoch
        self.epoch_value = epoch.get()

# ################################################################################################################################

    def get_epoch(self) -> 'int':
        """ Returns the current payload epoch, dropping every payload kept if an edit advanced it.
        """
        out = self.epoch.get()

        if out != self.epoch_value:
            self._payloads.clear()
            self.size = 0
            self.epoch_value = out

        return out

# ################################################################################################################################

    def get(self, msg_id:'str') -> 'strnone':
        """ Returns the payload of a message, or None if it is not kept.
        """
        _ = self.get_epoch()

        entry = self._payloads.get(msg_id)

        if entry is None:
            return None

        self._payloads.move_to_end(msg_id)

        payload, _ = entry
        return payload

# ################################################################################################################################

    def put(self, msg_id:'str', payload:'str', size:'int', read_epoch:'int') -> 'None':
        """ Keeps the payload of a message read under the given epoch, dropping those used least recently
        once the total size is exceeded.
        """
        # A payload read before an edit advanced the epoch may be the one that the edit replaced ..
        if self.get_epoch() != read_epoch:
            return

        # .. a payload larger than the whole cache is not kept ..
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

    def invalidate(self) -> 'None':
        """ Advances the payload epoch after an edit committed, so that each payload is read from the database
        on the next delivery.
        """
        self.epoch.advance()

# ################################################################################################################################
# ################################################################################################################################
