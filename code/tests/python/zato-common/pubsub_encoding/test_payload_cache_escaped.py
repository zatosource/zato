# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
import gevent

# Zato
from zato.common.pubsub.sql.payload_cache import PayloadCache, PayloadEpoch

# Zato - Rust
from zato_common_core.zato_common_core import escape_push_payload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet

    greenletlist = list[Greenlet]

# ################################################################################################################################
# ################################################################################################################################

_msg_id = 'zpsm.0192d3a1b2c3d4e5f60718293a4b5c6d'
_other_msg_id = 'zpsm.0192d3a1b2c3d4e5f60718293a4b5c6e'

# How many pushes of one message escape its payload at the same time
_concurrent_push_count = 200

# The size of the payload of the concurrent pushes
_large_payload_size = 8 * 1024 * 1024

# The size of the cache of the tests of size accounting
_small_cache_size = 1000

# How many pushes of one message wait for an escaping that fails
_failed_push_count = 3

# The code points of the control characters, which JSON strings escape into six bytes each
_control_characters_end = 0x20

# ################################################################################################################################
# ################################################################################################################################

class _EscapeError(Exception):
    """ The error of an escaping that a test makes fail.
    """

# ################################################################################################################################
# ################################################################################################################################

class _CountingEscape:
    """ Escapes payloads as push delivery does, counting each escaping. It can be made to fail its first escaping
    or to advance the payload epoch while the escaping runs.
    """
    def __init__(self, *, fails_first:'bool'=False, epoch:'PayloadEpoch | None'=None) -> 'None':
        self.call_count = 0
        self.fails_first = fails_first
        self.epoch = epoch

    def __call__(self, payload:'str') -> 'bytes':
        self.call_count += 1

        # The first escaping fails ..
        if self.fails_first:
            if self.call_count == 1:
                raise _EscapeError(f'Escaping of a payload of {len(payload)} characters failed')

        # .. or an edit commits while the payload is escaped ..
        if self.epoch:
            self.epoch.advance()

        # .. and otherwise the payload is escaped.
        out = escape_push_payload(payload)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_payload(text:'str', size:'int') -> 'str':
    """ Returns a payload of the given size, a new object each time.
    """
    repeat_count = size // len(text) + 1
    out = text * repeat_count
    out = out[:size]
    return out

# ################################################################################################################################

def _new_payload_of_control_characters(size:'int') -> 'str':
    """ Returns a payload that JSON escapes into six times its size.
    """
    out = ''

    for _ in range(size):
        out += chr(0)

    return out

# ################################################################################################################################

def _new_cache(max_size:'int', escape:'_CountingEscape') -> 'PayloadCache':
    out = PayloadCache(max_size, PayloadEpoch(), escape)
    return out

# ################################################################################################################################

def _put(cache:'PayloadCache', msg_id:'str', payload:'str') -> 'None':
    read_epoch = cache.get_epoch()
    payload_size = len(payload)
    cache.put(msg_id, payload, payload_size, read_epoch)

# ################################################################################################################################

def _spawn_pushes(cache:'PayloadCache', payload:'str', push_count:'int') -> 'greenletlist':
    """ Starts the given number of pushes of one message, each of which escapes its payload, and waits for all of them.
    """
    out:'greenletlist' = []

    for _ in range(push_count):
        greenlet = gevent.spawn(cache.get_escaped, _msg_id, payload)
        out.append(greenlet)

    _ = gevent.joinall(out)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_concurrent_pushes_escape_a_payload_once() -> 'None':
    escape = _CountingEscape()
    cache = _new_cache(_large_payload_size * 8, escape)

    payload = _new_payload('Order "12345" for John Smith\n', _large_payload_size)
    _put(cache, _msg_id, payload)

    pushes = _spawn_pushes(cache, payload, _concurrent_push_count)

    # The payload is escaped by one push alone ..
    assert escape.call_count == 1

    # .. every push receives the same escaped payload ..
    first_push = pushes[0]
    expected = first_push.value

    for push in pushes:
        assert push.successful()
        assert push.value is expected

    assert expected == escape_push_payload(payload)

    # .. and a later push uses it without escaping the payload again.
    escaped = cache.get_escaped(_msg_id, payload)

    assert escaped is expected
    assert escape.call_count == 1

# ################################################################################################################################

def test_an_edited_payload_is_escaped_without_being_kept() -> 'None':
    escape = _CountingEscape()
    cache = _new_cache(_small_cache_size, escape)

    payload = _new_payload('Order 12345 for John Smith', 100)
    _put(cache, _msg_id, payload)

    size_before = cache.size

    # A payload read again after an edit is a different object than the payload kept, so its escaped form is not kept ..
    edited = _new_payload('Order 12345 for Maria Johnson', 100)
    escaped = cache.get_escaped(_msg_id, edited)

    assert escaped == escape_push_payload(edited)
    assert cache.size == size_before

    # .. the payload kept is escaped and kept the first time a push needs it ..
    escaped = cache.get_escaped(_msg_id, payload)

    assert escaped == escape_push_payload(payload)
    assert cache.size == size_before + len(escaped)

    # .. and an edit drops it together with its escaped form, after which nothing is kept for the message.
    cache.invalidate()
    escaped = cache.get_escaped(_msg_id, payload)

    assert escaped == escape_push_payload(payload)
    assert cache.get(_msg_id) is None
    assert cache.size == 0
    assert escape.call_count == 3

# ################################################################################################################################

def test_an_edit_during_an_escaping_leaves_nothing_kept() -> 'None':
    epoch = PayloadEpoch()
    escape = _CountingEscape(epoch=epoch)
    cache = PayloadCache(_small_cache_size, epoch, escape)

    payload = _new_payload('Invoice 2026-001 for Anna Miller', 100)
    _put(cache, _msg_id, payload)

    # The edit commits while the payload is escaped, so the payload kept may be the one that the edit replaced
    escaped = cache.get_escaped(_msg_id, payload)

    assert escaped == escape_push_payload(payload)
    assert cache.get(_msg_id) is None
    assert cache.size == 0

# ################################################################################################################################

def test_the_size_counts_the_escaped_payloads() -> 'None':
    escape = _CountingEscape()
    cache = _new_cache(_small_cache_size, escape)

    first = _new_payload('Order 12345 for John Smith', 300)
    second = _new_payload('Order 12346 for Jane Doe', 300)

    _put(cache, _msg_id, first)
    _put(cache, _other_msg_id, second)

    # The escaped form of a payload is counted with the payload ..
    escaped = cache.get_escaped(_msg_id, first)
    assert cache.size == len(first) + len(escaped) + len(second)

    # .. the payloads used least recently leave once the escaped forms exceed the size ..
    escaped = cache.get_escaped(_other_msg_id, second)

    assert cache.size <= _small_cache_size
    assert cache.get(_msg_id) is None
    assert cache.get(_other_msg_id) is second

    # .. and a payload whose escaped form does not fit in the cache with it is returned without being kept.
    cache.invalidate()

    payload = _new_payload_of_control_characters(_small_cache_size // 4)
    _put(cache, _msg_id, payload)

    escaped = cache.get_escaped(_msg_id, payload)

    assert escaped == escape_push_payload(payload)
    assert len(payload) + len(escaped) > _small_cache_size
    assert cache.size == len(payload)

# ################################################################################################################################

def test_a_failed_escaping_fails_every_push_waiting_for_it() -> 'None':
    escape = _CountingEscape(fails_first=True)
    cache = _new_cache(_small_cache_size, escape)

    payload = _new_payload('Order 12345 for John Smith', 100)
    _put(cache, _msg_id, payload)

    pushes = _spawn_pushes(cache, payload, _failed_push_count)

    # Every push waiting for the escaping receives its error ..
    for push in pushes:
        assert isinstance(push.exception, _EscapeError)

    assert escape.call_count == 1

    # .. and the next push escapes the payload again.
    escaped = cache.get_escaped(_msg_id, payload)

    assert escaped == escape_push_payload(payload)
    assert escape.call_count == 2

# ################################################################################################################################
# ################################################################################################################################
