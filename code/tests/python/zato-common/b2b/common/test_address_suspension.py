# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ssl
from datetime import timedelta
from email.message import Message
from http.client import BAD_GATEWAY, GATEWAY_TIMEOUT, INTERNAL_SERVER_ERROR, OK, SERVICE_UNAVAILABLE
from urllib.error import HTTPError, URLError

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.b2b.common.address_state import AddressRegistry, AddressState, Default_Probe_Interval_Seconds, \
    Default_Suspend_After_Failures, Env_Probe_Interval_Seconds, Env_Suspend_After_Failures, is_transport_error, \
    is_transport_failure_status, SuspensionReason
from zato.common.b2b.common.clock import ManualClock
from zato.common.b2b.common.outcome import FailureCause, FinalState
from zato.common.b2b.common.retry import next_action, RetryAction, RetryPolicy, RetryState
from zato.common.b2b.common.store import new_memory_store
from zato.common.b2b.ebms2.common import MSHService
from zato.common.b2b.ebms2.outbound import expire_suspended
from zato.common.b2b.ebms2.probe import build_ping, is_pong
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import answer, deliver, new_exchange, resolve, send, Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from pytest import MonkeyPatch
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import strlist
    datetime = datetime
    MonkeyPatch = MonkeyPatch
    strlist = strlist
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_server_name = 'b2b-test-server'
_address = 'https://partner.example.com/ebms'
_other_address = 'https://other.example.com/ebms'

_operator_reason = 'Partner maintenance window'

# The retries of the policy of the hold tests and their interval, in seconds.
_retries = 3
_retry_interval_seconds = 30

# A threshold other than the default.
_custom_failures = 2

# ################################################################################################################################
# ################################################################################################################################

def _registry() -> 'AddressRegistry':
    store = new_memory_store()

    out = AddressRegistry(store.writer, AuditSource.EbMS2, _server_name, ManualClock(Start_Time))
    return out

# ################################################################################################################################

def _event_types(registry:'AddressRegistry') -> 'strlist':
    statement = select(event_table.c.event_type).order_by(event_table.c.id)

    out:'strlist' = []

    with registry.writer.engine.connect() as connection:
        for event_type in connection.execute(statement).scalars():
            out.append(event_type)

    return out

# ################################################################################################################################

def _fail(registry:'AddressRegistry', count:'int') -> 'list[bool]':
    """ Records consecutive transport failures of the address and returns what each one returned.
    """
    out:'list[bool]' = []

    for _ in range(count):
        is_suspended = registry.record_failure(_address)
        out.append(is_suspended)

    return out

# ################################################################################################################################

def _policy() -> 'RetryPolicy':
    out = RetryPolicy()
    out.retries = _retries
    out.retry_interval = timedelta(seconds=_retry_interval_seconds)

    return out

# ################################################################################################################################

def _state() -> 'RetryState':
    """ Returns the state of a message after its first delivery, whose interval has passed.
    """
    out = RetryState()
    out.attempt_count = 1
    out.last_attempt_at = Start_Time

    return out

# ################################################################################################################################

def _after(seconds:'int') -> 'datetime':
    out = Start_Time + timedelta(seconds=seconds)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestClassification:
    """ A connection error, a TLS error, a timeout or a gateway status is a transport failure, and nothing else is.
    """

    def test_statuses(self) -> 'None':
        assert is_transport_failure_status(BAD_GATEWAY)
        assert is_transport_failure_status(SERVICE_UNAVAILABLE)
        assert is_transport_failure_status(GATEWAY_TIMEOUT)

        assert not is_transport_failure_status(OK)
        assert not is_transport_failure_status(INTERNAL_SERVER_ERROR)

    def test_errors(self) -> 'None':
        assert is_transport_error(ConnectionRefusedError())
        assert is_transport_error(ConnectionResetError())
        assert is_transport_error(ssl.SSLError())
        assert is_transport_error(TimeoutError())
        assert is_transport_error(URLError('Name or service not known'))

        unavailable = HTTPError(_address, SERVICE_UNAVAILABLE, 'Service Unavailable', Message(), None)
        server_error = HTTPError(_address, INTERNAL_SERVER_ERROR, 'Internal Server Error', Message(), None)

        assert is_transport_error(unavailable)
        assert not is_transport_error(server_error)
        assert not is_transport_error(ValueError())

# ################################################################################################################################
# ################################################################################################################################

class TestSuspension:
    """ An address is suspended after a run of transport failures, and a response of any other kind ends the run.
    """

    def test_defaults(self) -> 'None':
        registry = _registry()

        assert registry.suspend_after == Default_Suspend_After_Failures
        assert registry.probe_interval == timedelta(seconds=Default_Probe_Interval_Seconds)

    def test_settings_from_environment(self, monkeypatch:'MonkeyPatch') -> 'None':
        monkeypatch.setenv(Env_Suspend_After_Failures, str(_custom_failures))
        monkeypatch.setenv(Env_Probe_Interval_Seconds, '15')

        registry = _registry()

        assert registry.suspend_after == _custom_failures
        assert registry.probe_interval == timedelta(seconds=15)

    def test_threshold(self) -> 'None':
        registry = _registry()

        before = Default_Suspend_After_Failures - 1
        expected = [False] * before
        expected.append(True)

        assert _fail(registry, Default_Suspend_After_Failures) == expected

        record = registry.get(_address)

        assert record.state == AddressState.Suspended
        assert record.consecutive_failures == Default_Suspend_After_Failures
        assert record.reason == SuspensionReason.Transport_Failures

        assert registry.is_suspended(_address)
        assert not registry.is_suspended(_other_address)
        assert registry.suspended() == [_address]

        # The suspension is recorded once, and further failures change nothing.
        assert not registry.record_failure(_address)
        assert _event_types(registry) == [AuditEvent.Delivery_Suspended]

    def test_counter_reset(self) -> 'None':
        registry = _registry()

        before = Default_Suspend_After_Failures - 1

        _ = _fail(registry, before)
        registry.record_success(_address)

        assert registry.get(_address).consecutive_failures == 0

        # The run starts over, so the same number of failures does not suspend the address.
        _ = _fail(registry, before)

        assert not registry.is_suspended(_address)
        assert _event_types(registry) == []

    def test_state_survives_a_restart(self) -> 'None':
        registry = _registry()

        _ = _fail(registry, Default_Suspend_After_Failures)

        restarted = AddressRegistry(registry.writer, AuditSource.EbMS2, _server_name, registry.clock)

        assert restarted.load() == 1
        assert restarted.is_suspended(_address)

# ################################################################################################################################
# ################################################################################################################################

class TestHold:
    """ A message to a suspended address is held without consuming its retries, and it still expires.
    """

    def test_hold_consumes_no_retries(self) -> 'None':
        policy = _policy()
        state = _state()

        now = _after(_retry_interval_seconds * 10)

        decision = next_action(policy, state, now, is_suspended=True)

        assert decision.action == RetryAction.Hold
        assert state.attempt_count == 1

        # Once the address is resumed, all the retries are still there.
        decision = next_action(policy, state, now)
        assert decision.action == RetryAction.Resend

    def test_hold_until_expiry(self) -> 'None':
        policy = _policy()
        state = _state()
        state.expires_at = _after(600)

        decision = next_action(policy, state, _after(60), is_suspended=True)

        assert decision.action == RetryAction.Hold
        assert decision.at == state.expires_at

    def test_expiry_while_suspended(self, parties:'TestParties') -> 'None':
        policy = _policy()
        state = _state()
        state.expires_at = _after(600)

        decision = next_action(policy, state, _after(600), is_suspended=True)

        assert decision.action == RetryAction.Give_Up

        # The exchange ends with the suspension as the cause of its failure.
        exchange = new_exchange(parties, new_settings(parties, Start_Time))
        outbound = send(exchange)

        expire_suspended(outbound)

        assert outbound.outcome.final_state == FinalState.Failed
        assert outbound.outcome.failure_cause == FailureCause.Address_Suspended

# ################################################################################################################################
# ################################################################################################################################

class TestResume:
    """ A Pong to a probe or an operator resumes an address, and an operator suspends one.
    """

    def test_probe(self, parties:'TestParties') -> 'None':
        registry = _registry()

        resumed:'strlist' = []
        registry.resume_callbacks.append(resumed.append)

        _ = _fail(registry, Default_Suspend_After_Failures)

        exchange = new_exchange(parties, new_settings(parties, Start_Time))
        binding = resolve(exchange, MSHService.Ping, is_msh=True)

        ping = build_ping(exchange.agreement, exchange.sender.local_keys, binding, exchange.clock)
        result = deliver(exchange, ping)
        _ = answer(exchange, ping, result)

        assert is_pong(ping)
        assert registry.record_probe(_address, is_pong(ping))

        assert not registry.is_suspended(_address)
        assert registry.get(_address).reason == SuspensionReason.Probe_Answered
        assert resumed == [_address]

        assert _event_types(registry) == [AuditEvent.Delivery_Suspended, AuditEvent.Delivery_Resumed]

    def test_unanswered_probe(self) -> 'None':
        registry = _registry()

        _ = _fail(registry, Default_Suspend_After_Failures)

        assert not registry.record_probe(_address, False)
        assert registry.is_suspended(_address)

    def test_operator(self) -> 'None':
        registry = _registry()

        resumed:'strlist' = []
        registry.resume_callbacks.append(resumed.append)

        registry.suspend(_address, _operator_reason)

        record = registry.get(_address)

        assert record.state == AddressState.Suspended
        assert record.reason == _operator_reason

        registry.resume(_address, _operator_reason)

        assert not registry.is_suspended(_address)
        assert resumed == [_address]
        assert _event_types(registry) == [AuditEvent.Delivery_Suspended, AuditEvent.Delivery_Resumed]

# ################################################################################################################################
# ################################################################################################################################
