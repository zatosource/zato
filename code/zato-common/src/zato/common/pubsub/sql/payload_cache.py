# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import OrderedDict

# gevent
from gevent import get_hub
from gevent.event import AsyncResult

# Zato
from zato.common.typing_ import cast_

# Zato - Rust
from zato_common_core.zato_common_core import escape_push_payload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import bytesnone, callable_, strnone

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

class PayloadCacheEntry:
    """ One payload kept by the cache, together with the payload escaped as a JSON string once the first push
    of its message escaped it. The size counts the payload and its escaped form alike.
    """
    __slots__ = ('payload', 'size', 'escaped', 'pending')

    def __init__(self, payload:'str', size:'int') -> 'None':
        self.payload = payload
        self.size = size
        self.escaped:'bytesnone' = None

        # The result of the escaping in progress, which the other pushes of the message wait for
        self.pending:'AsyncResult | None' = None

# ################################################################################################################################
# ################################################################################################################################

class PayloadCache:
    """ The payloads of the messages that push delivery read most recently, up to a total size, by the identifier
    of each message. A message pushed to many subscribers is read from the database and decrypted once
    rather than once per subscriber, and its payload is escaped into JSON once rather than once per subscriber.
    A payload changes only through an edit of its message, which advances the payload epoch, after which the cache
    drops the payloads it keeps.
    """

    def __init__(self, max_size:'int', epoch:'PayloadEpoch', escape:'callable_'=escape_push_payload) -> 'None':
        self.max_size = max_size
        self.size = 0
        self._payloads:'OrderedDict[str, PayloadCacheEntry]' = OrderedDict()

        # The function that escapes a payload into a JSON string, run in a thread of the pool
        self._escape = escape

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

        out = entry.payload
        return out

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

        self._payloads[msg_id] = PayloadCacheEntry(payload, size)
        self.size += size

        self._evict()

# ################################################################################################################################

    def get_escaped(self, msg_id:'str', payload:'str') -> 'bytes':
        """ Returns the payload of a message escaped as a JSON string. A payload kept by the cache is escaped once
        and the result is shared by every push of its message, including the pushes that wait for an escaping
        in progress. Any other payload is escaped for this push alone.
        """
        _ = self.get_epoch()

        entry = self._payloads.get(msg_id)

        # A payload that is not kept is escaped without being kept ..
        if entry is None:
            out = self._escape_in_pool(payload)
            return out

        # .. and so is one other than the payload kept, e.g. one read again after an edit ..
        if entry.payload is not payload:
            out = self._escape_in_pool(payload)
            return out

        self._payloads.move_to_end(msg_id)

        # .. a payload escaped already is shared ..
        if escaped := entry.escaped:
            return escaped

        # .. a payload that another push is escaping is awaited ..
        if pending := entry.pending:
            escaped = pending.get()

            out = cast_('bytes', escaped)
            return out

        # .. and otherwise this push escapes the payload for every other push of the message.
        pending = AsyncResult()
        entry.pending = pending

        try:
            out = self._escape_in_pool(payload)
        except Exception as e:
            entry.pending = None
            pending.set_exception(e)
            raise

        entry.pending = None
        pending.set(out)

        self._keep_escaped(msg_id, entry, out)

        return out

# ################################################################################################################################

    def invalidate(self) -> 'None':
        """ Advances the payload epoch after an edit committed, so that each payload is read from the database
        on the next delivery.
        """
        self.epoch.advance()

# ################################################################################################################################

    def _escape_in_pool(self, payload:'str') -> 'bytes':
        """ Escapes a payload in a thread of the pool, which writes the JSON without the GIL,
        so that the event loop serves other requests while the payload is escaped.
        """
        hub = get_hub()

        out = hub.threadpool.apply(self._escape, (payload,))
        return out

# ################################################################################################################################

    def _keep_escaped(self, msg_id:'str', entry:'PayloadCacheEntry', escaped:'bytes') -> 'None':
        """ Keeps the escaped form of a payload with the payload itself, if the entry is still kept
        and both of them fit in the cache together.
        """
        _ = self.get_epoch()

        # An edit dropped the entry or an eviction removed it while the payload was escaped ..
        if self._payloads.get(msg_id) is not entry:
            return

        escaped_size = len(escaped)
        entry_size = entry.size + escaped_size

        # .. and an entry larger than the whole cache is not kept with its escaped form.
        if entry_size > self.max_size:
            return

        entry.escaped = escaped
        entry.size = entry_size
        self.size += escaped_size

        self._evict()

# ################################################################################################################################

    def _evict(self) -> 'None':
        """ Drops the payloads used least recently until the total size is within the limit.
        """
        while self.size > self.max_size:
            _, evicted = self._payloads.popitem(last=False)
            self.size -= evicted.size

# ################################################################################################################################
# ################################################################################################################################
