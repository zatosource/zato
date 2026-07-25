# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.soap.common import NS, SOAPSecurityException, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.soap.security.replay import ReplayCache, replay_cache
from zato.common.soap.security.usernametoken import _compute_digest as compute_digest, add_username_token, \
    Clock_Skew_Seconds, Created_TTL_Seconds, verify_username_token
from zato.common.soap.security.x509 import add_timestamp, sign, Timestamp_TTL_Seconds, validate_timestamp, verify
from zato.common.util.xml_.core import qname, to_timestamp
from zato.common.util.xml_.xmlsec import decode_base64

# ################################################################################################################################
# ################################################################################################################################

_username = 'MYUSER'
_password = 'MYPASS'

# ################################################################################################################################
# ################################################################################################################################

def fail_message(expected):
    """ Asserts that the block raises a security exception whose message names the expected reason.

    Every case here has a specific reason for being refused, and a test that only checks that
    something was raised would pass for the wrong reason - a typo in a namespace, say, refuses the
    message just as thoroughly as the rule under test does.
    """
    out = pytest.raises(SOAPSecurityException, match=expected)
    return out

# ################################################################################################################################

def _recompute_digest(token, created_text):
    """ Recomputes a digest token's password over a creation time that has been changed.

    The digest covers the creation time, so a test that moves the time has to recompute it - which
    is what a sender with a differing clock does anyway.
    """
    nonce_text = token.find(qname(NS.WSSE, 'Nonce')).text
    nonce = decode_base64(nonce_text)

    token.find(qname(NS.WSSE, 'Password')).text = compute_digest(nonce, created_text, _password)

# ################################################################################################################################

def _reparse(envelope):
    """ Serializes and reparses an envelope, as would happen over the wire.
    """
    out = etree.fromstring(to_bytes(envelope))
    return out

# ################################################################################################################################

def _sample_envelope():
    """ A SOAP 1.2 envelope with a small business body.
    """
    request = SOAPMessage()
    request.namespace = 'urn:example:invoicing'
    request.InvoiceNumber = 'INV-2026-0401'

    envelope = build_envelope(SOAPVersion.V12)
    _ = attach_body(envelope, request, 'SubmitInvoice')

    return envelope

# ################################################################################################################################

def _set_window(timestamp, created_offset_seconds, ttl_seconds=Timestamp_TTL_Seconds):
    """ Rewrites a wsu:Timestamp so its window opens the given number of seconds from now -
    negative for the past, positive for the future.
    """
    created = datetime.now(timezone.utc) + timedelta(seconds=created_offset_seconds)
    expires = created + timedelta(seconds=ttl_seconds)

    timestamp.find(qname(NS.WSU, 'Created')).text = to_timestamp(created)
    timestamp.find(qname(NS.WSU, 'Expires')).text = to_timestamp(expires)

# ################################################################################################################################

def _timestamp_of(envelope):
    out = envelope.find(f'.//{qname(NS.WSU, "Timestamp")}')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestTimestampValidation:
    """ The wsu:Timestamp validity window.

    Nothing else on the inbound path is time-bounded, so without this a captured message replays
    for as long as the signing certificate stays valid, which is measured in years.
    """

    def test_a_fresh_timestamp_is_accepted(self):
        envelope = _sample_envelope()
        _ = add_timestamp(envelope)

        validate_timestamp(_timestamp_of(envelope))

    def test_an_expired_timestamp_is_refused(self):
        envelope = _sample_envelope()
        _ = add_timestamp(envelope)

        # Well past the window, and past the skew allowance on top of it.
        _set_window(_timestamp_of(envelope), -(Timestamp_TTL_Seconds + Clock_Skew_Seconds + 60))

        with pytest.raises(SOAPSecurityException) as e:
            validate_timestamp(_timestamp_of(envelope))

        assert 'has expired' in str(e.value)

    def test_a_timestamp_from_the_future_is_refused(self):
        # A message minted with a Created in the future stays valid for longer than its
        # time-to-live allows, which is a way to extend the replay window at will.
        envelope = _sample_envelope()
        _ = add_timestamp(envelope)

        _set_window(_timestamp_of(envelope), Clock_Skew_Seconds + 60)

        with fail_message('created too far in the future'):
            validate_timestamp(_timestamp_of(envelope))

    def test_a_clock_slightly_ahead_is_tolerated(self):
        # Two peers' clocks are never exactly aligned, so a message that looks a little early is
        # accepted - refusing it would break every peer whose clock runs a second fast.
        envelope = _sample_envelope()
        _ = add_timestamp(envelope)

        _set_window(_timestamp_of(envelope), Clock_Skew_Seconds - 10)

        validate_timestamp(_timestamp_of(envelope))

    def test_a_message_just_expired_is_tolerated_within_the_skew(self):
        envelope = _sample_envelope()
        _ = add_timestamp(envelope)

        _set_window(_timestamp_of(envelope), -(Timestamp_TTL_Seconds + 10))

        validate_timestamp(_timestamp_of(envelope))

    def test_an_expiry_before_the_creation_is_refused(self):
        # Not a window at all. Both of the checks above pass for a message whose Expires precedes
        # its Created by less than the skew, so the ordering is checked in its own right.
        envelope = _sample_envelope()
        _ = add_timestamp(envelope)

        timestamp = _timestamp_of(envelope)
        now = datetime.now(timezone.utc)

        timestamp.find(qname(NS.WSU, 'Created')).text = to_timestamp(now)
        timestamp.find(qname(NS.WSU, 'Expires')).text = to_timestamp(now - timedelta(seconds=10))

        with fail_message('expires before it was created'):
            validate_timestamp(timestamp)

    def test_a_timestamp_without_an_expiry_is_refused(self):
        # A message that declares no expiry cannot be said to have not expired, so treating an
        # absent Expires as "still valid" would defeat the whole check.
        envelope = _sample_envelope()
        _ = add_timestamp(envelope)

        timestamp = _timestamp_of(envelope)
        timestamp.remove(timestamp.find(qname(NS.WSU, 'Expires')))

        with fail_message('no Expires'):
            validate_timestamp(timestamp)

    def test_a_timestamp_without_a_creation_time_is_refused(self):
        envelope = _sample_envelope()
        _ = add_timestamp(envelope)

        timestamp = _timestamp_of(envelope)
        timestamp.remove(timestamp.find(qname(NS.WSU, 'Created')))

        with fail_message('no Created'):
            validate_timestamp(timestamp)

    def test_an_unparseable_timestamp_is_refused(self):
        envelope = _sample_envelope()
        _ = add_timestamp(envelope)

        timestamp = _timestamp_of(envelope)
        timestamp.find(qname(NS.WSU, 'Created')).text = 'last Tuesday'

        with pytest.raises(SOAPSecurityException):
            validate_timestamp(timestamp)

    def test_an_expired_message_is_refused_by_verification(self, parties):
        # The window is checked as part of verifying, not only in isolation, and it is checked after
        # the signature - an unsigned timestamp says whatever the sender wants it to say, so reading
        # one before it is known to be covered would be reading the attacker's own claim.
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        wire = _reparse(envelope)
        _set_window(_timestamp_of(wire), -(Timestamp_TTL_Seconds + Clock_Skew_Seconds + 60))

        with pytest.raises(SOAPSecurityException):
            _ = verify(wire, parties.receiver)

# ################################################################################################################################
# ################################################################################################################################

class TestNonceReplay:
    """ The wsse:Nonce of a digest UsernameToken, which is what stops a captured token being
    presented twice inside its own validity window.
    """

    def test_a_token_is_accepted_once(self):
        envelope = _sample_envelope()
        _ = add_username_token(envelope, _username, _password, use_digest=True)

        verify_username_token(_reparse(envelope), _username, _password, use_digest=True)

    def test_the_same_token_is_refused_the_second_time(self):
        envelope = _sample_envelope()
        _ = add_username_token(envelope, _username, _password, use_digest=True)

        wire = to_bytes(envelope)

        # The very same bytes twice, which is exactly what a captured message replayed is.
        verify_username_token(etree.fromstring(wire), _username, _password, use_digest=True)

        with fail_message('Nonce has already been used'):
            verify_username_token(etree.fromstring(wire), _username, _password, use_digest=True)

    def test_two_separate_tokens_are_both_accepted(self):
        # Each token gets its own nonce, so two genuine requests from the same client with the same
        # credentials are two different one-shot values and neither is a replay of the other.
        for _ in range(2):
            envelope = _sample_envelope()
            _ = add_username_token(envelope, _username, _password, use_digest=True)

            verify_username_token(_reparse(envelope), _username, _password, use_digest=True)

    def test_a_token_with_no_nonce_is_refused(self):
        # Without a nonce there is nothing to remember, so a token that omits one would be
        # replayable for the whole of its Created window.
        envelope = _sample_envelope()
        token = add_username_token(envelope, _username, _password, use_digest=True)
        token.remove(token.find(qname(NS.WSSE, 'Nonce')))

        with fail_message('no Nonce'):
            verify_username_token(_reparse(envelope), _username, _password, use_digest=True)

    def test_a_token_with_an_empty_nonce_is_refused(self):
        envelope = _sample_envelope()
        token = add_username_token(envelope, _username, _password, use_digest=True)
        token.find(qname(NS.WSSE, 'Nonce')).text = None

        with fail_message('empty Nonce'):
            verify_username_token(_reparse(envelope), _username, _password, use_digest=True)

    def test_a_token_with_a_malformed_nonce_is_refused(self):
        envelope = _sample_envelope()
        token = add_username_token(envelope, _username, _password, use_digest=True)
        token.find(qname(NS.WSSE, 'Nonce')).text = 'not base64 at all !!!'

        with fail_message('malformed Nonce'):
            verify_username_token(_reparse(envelope), _username, _password, use_digest=True)

# ################################################################################################################################
# ################################################################################################################################

class TestCreatedWindow:
    """ The wsu:Created of a digest UsernameToken, which bounds how long a captured token is worth
    replaying at all. The nonce cache stops the second use, and this is what stops the cache having
    to remember a value indefinitely.
    """

    def test_a_stale_token_is_refused(self):
        envelope = _sample_envelope()
        token = add_username_token(envelope, _username, _password, use_digest=True)

        created = datetime.now(timezone.utc) - timedelta(seconds=Created_TTL_Seconds + Clock_Skew_Seconds + 60)
        token.find(qname(NS.WSU, 'Created')).text = to_timestamp(created)

        with fail_message('too old'):
            verify_username_token(_reparse(envelope), _username, _password, use_digest=True)

    def test_a_token_from_the_future_is_refused(self):
        envelope = _sample_envelope()
        token = add_username_token(envelope, _username, _password, use_digest=True)

        created = datetime.now(timezone.utc) + timedelta(seconds=Clock_Skew_Seconds + 60)
        token.find(qname(NS.WSU, 'Created')).text = to_timestamp(created)

        with fail_message('created too far in the future'):
            verify_username_token(_reparse(envelope), _username, _password, use_digest=True)

    def test_a_token_within_the_window_is_accepted(self):
        envelope = _sample_envelope()
        token = add_username_token(envelope, _username, _password, use_digest=True)

        created = datetime.now(timezone.utc) - timedelta(seconds=Created_TTL_Seconds // 2)
        created_text = to_timestamp(created)
        token.find(qname(NS.WSU, 'Created')).text = created_text

        # The digest covers the creation time, so moving it means recomputing the digest - which is
        # what a sender whose clock differs does anyway.
        _recompute_digest(token, created_text)

        verify_username_token(_reparse(envelope), _username, _password, use_digest=True)

    def test_the_creation_time_is_checked_before_the_digest(self):
        # A stale token is refused for being stale whether or not its password is right, so an
        # attacker replaying a captured token learns nothing about the credentials from the answer.
        envelope = _sample_envelope()
        token = add_username_token(envelope, _username, 'THE-WRONG-PASSWORD', use_digest=True)

        created = datetime.now(timezone.utc) - timedelta(seconds=Created_TTL_Seconds + Clock_Skew_Seconds + 60)
        token.find(qname(NS.WSU, 'Created')).text = to_timestamp(created)

        with fail_message('too old'):
            verify_username_token(_reparse(envelope), _username, _password, use_digest=True)

# ################################################################################################################################
# ################################################################################################################################

class TestReplayCache:
    """ The cache itself. An unauthenticated caller decides how many values arrive, so it has to
    have a ceiling, and it has to forget values once the messages carrying them would be refused on
    their own merits anyway.
    """

    def test_a_value_is_accepted_once(self):
        cache = ReplayCache()
        cache.check_and_add('key-1', 'Nonce')

        with fail_message('Nonce has already been used'):
            cache.check_and_add('key-1', 'Nonce')

    def test_different_values_do_not_collide(self):
        cache = ReplayCache()

        for i in range(100):
            cache.check_and_add(f'key-{i}', 'Nonce')

        assert len(cache) == 100

    def test_an_expired_value_is_forgotten(self):
        # A replay is worth refusing only for as long as the message carrying it would be accepted
        # on its own merits, so once the time-to-live has passed the value need not be remembered.
        cache = ReplayCache(ttl_seconds=0)
        cache.check_and_add('key-1', 'Nonce')

        # With no time-to-live at all the entry is already expired, so the same value is not a
        # replay - and the entry itself is gone rather than merely being ignored.
        cache.check_and_add('key-1', 'Nonce')
        assert len(cache) == 1

    def test_the_cache_is_bounded(self):
        # Without a ceiling an unauthenticated caller sending distinct nonces is a way to exhaust
        # the worker's memory, one request at a time.
        cache = ReplayCache(max_size=10)

        for i in range(50):
            cache.check_and_add(f'key-{i}', 'Nonce')

        assert len(cache) == 10

    def test_the_oldest_values_are_the_ones_forgotten(self):
        cache = ReplayCache(max_size=3)

        for i in range(5):
            cache.check_and_add(f'key-{i}', 'Nonce')

        # The three most recent are still remembered, so replaying one of them is refused ..
        for i in (2, 3, 4):
            with pytest.raises(SOAPSecurityException):
                cache.check_and_add(f'key-{i}', 'Nonce')

        # .. and the two oldest were dropped, which is the same outcome their time-to-live would
        # have produced a moment later.
        assert len(cache) == 3

    def test_what_a_value_is_reports_itself(self):
        # The cache holds nonces and assertion ids together, so the message has to say which kind
        # of value was replayed or an operator reading the log cannot tell them apart.
        cache = ReplayCache()
        cache.check_and_add('key-1', 'Assertion')

        with fail_message('Assertion has already been used'):
            cache.check_and_add('key-1', 'Assertion')

    def test_the_shared_cache_is_one_instance(self):
        # A per-definition cache would let the same nonce through once per definition, and a
        # per-request one would not remember anything at all.
        from zato.common.soap.security import usernametoken

        assert usernametoken.replay_cache is replay_cache

# ################################################################################################################################
# ################################################################################################################################
