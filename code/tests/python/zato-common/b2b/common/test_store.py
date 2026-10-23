# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# gevent
from gevent import joinall, spawn

# pytest
import pytest

# Zato
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.common.store import HeldMessage, MessageIdentity, new_memory_store, StoredMessage, StoredResponse

# ################################################################################################################################
# ################################################################################################################################

bool_list = list[bool]

# ################################################################################################################################
# ################################################################################################################################

_now = datetime(2026, 1, 1, tzinfo=timezone.utc)

_protocol = 'ebms2'
_from_party = 'b2b-partner'
_to_party = 'b2b-host'
_conversation = 'b2b-conversation'

_persist_seconds = 60

_greenlet_count = 20

# ################################################################################################################################
# ################################################################################################################################

def _identity(message_id:'str') -> 'MessageIdentity':
    out = MessageIdentity(_protocol, _from_party, _to_party, message_id)
    return out

# ################################################################################################################################

def _message(received_at:'datetime') -> 'StoredMessage':

    response = StoredResponse()
    response.status_code = 200
    response.content_type = 'text/xml'
    response.body = b'<Acknowledgment/>'
    response.is_synchronous = True

    out = StoredMessage()
    out.status = 'Received'
    out.received_at = received_at
    out.expires_at = received_at + timedelta(seconds=_persist_seconds)
    out.response = response

    return out

# ################################################################################################################################

def _held(body:'bytes') -> 'HeldMessage':
    out = HeldMessage()
    out.content_type = 'text/xml'
    out.body = body

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMessageStore:

    def test_claim_records_a_message_once(self) -> 'None':
        store = new_memory_store()
        identity = _identity('message-1')

        assert store.claim(identity, _message(_now), _now)
        assert not store.claim(identity, _message(_now), _now)

        stored = store.get(identity, _now)

        assert stored is not None
        assert stored.response.body == b'<Acknowledgment/>'

    def test_expired_record_is_replaced(self) -> 'None':
        store = new_memory_store()
        identity = _identity('message-1')

        later = _now + timedelta(seconds=_persist_seconds)

        assert store.claim(identity, _message(_now), _now)
        assert store.get(identity, later) is None
        assert store.claim(identity, _message(later), later)

    def test_status_of_claimed_message(self) -> 'None':
        store = new_memory_store()
        identity = _identity('message-1')

        _ = store.claim(identity, _message(_now), _now)
        store.set_status(identity, 'Processed')

        stored = store.get(identity, _now)

        assert stored is not None
        assert stored.status == 'Processed'

    def test_status_of_unclaimed_message(self) -> 'None':
        store = new_memory_store()
        identity = _identity('message-1')

        with pytest.raises(B2BException):
            store.set_status(identity, 'Processed')

    def test_held_message_keeps_first_copy(self) -> 'None':
        store = new_memory_store()

        store.hold(_conversation, 2, _held(b'first'))
        store.hold(_conversation, 2, _held(b'second'))

        released = store.release(_conversation, 2)

        assert released is not None
        assert released.body == b'first'
        assert store.release(_conversation, 2) is None

    def test_next_sequence(self) -> 'None':
        store = new_memory_store()

        assert store.get_next_sequence(_conversation) is None

        store.set_next_sequence(_conversation, 1)
        store.set_next_sequence(_conversation, 2)

        assert store.get_next_sequence(_conversation) == 2

    def test_stores_are_separate(self) -> 'None':
        first = new_memory_store()
        second = new_memory_store()
        identity = _identity('message-1')

        _ = first.claim(identity, _message(_now), _now)

        assert second.get(identity, _now) is None

    def test_store_is_shared_by_greenlets(self) -> 'None':
        store = new_memory_store()
        identity = _identity('message-1')

        results:'bool_list' = []

        def claim() -> 'None':
            is_claimed = store.claim(identity, _message(_now), _now)
            results.append(is_claimed)

        greenlets = [spawn(claim) for _ in range(_greenlet_count)]
        _ = joinall(greenlets, raise_error=True)

        # Exactly one of the greenlets records the message, and every other one finds it recorded.
        assert results.count(True) == 1
        assert store.get(identity, _now) is not None

# ################################################################################################################################
# ################################################################################################################################
