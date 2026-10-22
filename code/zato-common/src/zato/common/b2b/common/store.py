# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from threading import Lock
from typing import NamedTuple, Protocol

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import strintdict
    datetime = datetime
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

class MessageIdentity(NamedTuple):
    """ What makes one received message the same message when it arrives again.
    """
    protocol:   str
    from_party: str
    to_party:   str
    message_id: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StoredResponse:
    """ The response signal that answered a received message, kept so that a duplicate gets the same one.
    """
    status_code:    int
    content_type:   str
    body:           bytes
    is_synchronous: bool

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StoredMessage:
    """ One received message as the store remembers it.
    """
    status:      str
    received_at: 'datetime'
    expires_at:  'datetime'
    response:    StoredResponse

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class HeldMessage:
    """ A received message whose delivery waits for the messages that precede it in its sequence.
    """
    content_type: str
    body:         bytes

# ################################################################################################################################
# ################################################################################################################################

held_message_dict = dict[tuple[str, int], HeldMessage]
stored_message_dict = dict[MessageIdentity, StoredMessage]

# ################################################################################################################################
# ################################################################################################################################

class MessageStore(Protocol):
    """ The state the B2B protocol layers keep between messages - received message identifiers
    with their responses and statuses, and the sequence state of ordered conversations.
    """

    def claim(self, identity:'MessageIdentity', message:'StoredMessage', now:'datetime') -> 'bool':
        """ Records a received message under its identity. Returns True when this call was the first
        to record it, and False when an unexpired record of the same identity exists already.
        """
        ...

    def get(self, identity:'MessageIdentity', now:'datetime') -> 'StoredMessage | None':
        """ Returns the unexpired record of a received message, or None.
        """
        ...

    def set_status(self, identity:'MessageIdentity', status:'str') -> 'None':
        """ Updates the status of a recorded message.
        """
        ...

    def get_next_sequence(self, conversation:'str') -> 'int | None':
        """ Returns the sequence number expected next in an ordered conversation, or None
        when the conversation has no state yet.
        """
        ...

    def set_next_sequence(self, conversation:'str', sequence_number:'int') -> 'None':
        """ Sets the sequence number expected next in an ordered conversation.
        """
        ...

    def hold(self, conversation:'str', sequence_number:'int', message:'HeldMessage') -> 'None':
        """ Keeps a message that arrived before the messages preceding it in its conversation.
        """
        ...

    def release(self, conversation:'str', sequence_number:'int') -> 'HeldMessage | None':
        """ Removes and returns the held message with the given sequence number, or None.
        """
        ...

# ################################################################################################################################
# ################################################################################################################################

class InMemoryMessageStore:
    """ A message store that keeps everything in the memory of the current process.
    """

    def __init__(self) -> 'None':
        self._lock = Lock()
        self._messages:'stored_message_dict' = {}
        self._sequences:'strintdict' = {}
        self._held:'held_message_dict' = {}

# ################################################################################################################################

    def claim(self, identity:'MessageIdentity', message:'StoredMessage', now:'datetime') -> 'bool':

        # Our response to produce
        out = True

        with self._lock:

            # An unexpired record means this is a duplicate ..
            if existing := self._messages.get(identity):
                if existing.expires_at > now:
                    out = False

            # .. otherwise the message is new, or its earlier record has expired.
            if out:
                self._messages[identity] = message

        return out

# ################################################################################################################################

    def get(self, identity:'MessageIdentity', now:'datetime') -> 'StoredMessage | None':

        # Our response to produce
        out = None

        with self._lock:
            if existing := self._messages.get(identity):
                if existing.expires_at > now:
                    out = existing

        return out

# ################################################################################################################################

    def set_status(self, identity:'MessageIdentity', status:'str') -> 'None':
        with self._lock:
            self._messages[identity].status = status

# ################################################################################################################################

    def get_next_sequence(self, conversation:'str') -> 'int | None':
        with self._lock:
            out = self._sequences.get(conversation)

        return out

# ################################################################################################################################

    def set_next_sequence(self, conversation:'str', sequence_number:'int') -> 'None':
        with self._lock:
            self._sequences[conversation] = sequence_number

# ################################################################################################################################

    def hold(self, conversation:'str', sequence_number:'int', message:'HeldMessage') -> 'None':
        key = (conversation, sequence_number)

        with self._lock:
            self._held[key] = message

# ################################################################################################################################

    def release(self, conversation:'str', sequence_number:'int') -> 'HeldMessage | None':
        key = (conversation, sequence_number)

        with self._lock:
            out = self._held.pop(key, None)

        return out

# ################################################################################################################################
# ################################################################################################################################
