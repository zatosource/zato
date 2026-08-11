# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from sqlalchemy import select

# Zato
from zato.common.alerting.collectors import collect_canary_facts, collect_certificate_facts, collect_health_facts
from zato.common.alerting.probes import normalize_health_state, parse_tls_target, run_canary_probe, \
    run_certificate_probe, run_health_probe
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import anylist
    anylist = anylist
    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-probes-server'

# ################################################################################################################################
# ################################################################################################################################

def _load_events(source:'str') -> 'anylist':
    """ Returns every stored event of one source, oldest first.
    """
    engine = get_audit_engine()

    statement = select(
        event_table.c.object_name,
        event_table.c.event_type,
        event_table.c.outcome,
        event_table.c.status,
    ).where(event_table.c.source == source).order_by(event_table.c.id)

    with engine.connect() as connection:
        out = connection.execute(statement).fetchall()

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestParseTLSTarget:

    def test_a_plain_https_address_gets_the_default_port(self) -> 'None':
        assert parse_tls_target('https://example.com/api/v1') == ('example.com', 443)

    def test_an_explicit_port_is_kept(self) -> 'None':
        assert parse_tls_target('https://example.com:8443/api') == ('example.com', 8443)

    def test_credentials_in_the_address_never_reach_the_handshake(self) -> 'None':
        assert parse_tls_target('https://user:secret@example.com:9443/x') == ('example.com', 9443)

    def test_an_address_that_does_not_speak_tls_yields_nothing(self) -> 'None':
        assert parse_tls_target('http://example.com') is None

# ################################################################################################################################
# ################################################################################################################################

class TestNormalizeHealthState:

    def test_the_provider_spellings_normalize(self) -> 'None':
        assert normalize_health_state('serviceDegradation') == 'degraded'
        assert normalize_health_state('ServiceInterruption') == 'interruption'

    def test_anything_unlisted_means_healthy(self) -> 'None':
        assert normalize_health_state('serviceOperational') == ''
        assert normalize_health_state('someFutureState') == ''

# ################################################################################################################################
# ################################################################################################################################

class TestCertificateProbe:

    def test_a_measured_target_writes_the_days_left_the_collector_reads(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # The remote side is faked - the probe's own bookkeeping is what runs for real
        def check(host:'str', port:'int', when:'datetime') -> 'float':
            assert host == 'crm.example.com'
            assert port == 443
            return 12.7

        targets = [{'object_name': 'CRM', 'host': 'crm.example.com', 'port': 443}]
        checked = run_certificate_probe(audit_log, targets, now, cid='cert-probe-1', check=check)

        assert checked == 1

        events = _load_events(AuditSource.Certificate)
        assert len(events) == 1
        assert events[0].object_name == 'CRM'
        assert events[0].event_type == AuditEvent.Cert_Checked
        assert events[0].outcome == AuditOutcome.OK

        # The collector surfaces the measure the probe wrote
        facts = collect_certificate_facts(engine, now)
        assert len(facts) == 1
        assert facts[0]['cert_days_left'] == 13

# ################################################################################################################################

    def test_one_target_failing_never_stops_the_others(self) -> 'None':
        audit_log = AuditLog(_server_name)
        now = utcnow()

        def check(host:'str', port:'int', when:'datetime') -> 'float':
            if host == 'down.example.com':
                raise Exception('Connection refused')
            return 90.0

        targets = [
            {'object_name': 'Down', 'host': 'down.example.com', 'port': 443},
            {'object_name': 'Up', 'host': 'up.example.com', 'port': 443},
        ]
        checked = run_certificate_probe(audit_log, targets, now, cid='cert-probe-2', check=check)

        assert checked == 2

        events = _load_events(AuditSource.Certificate)
        by_name = {event.object_name: event for event in events}

        assert by_name['Down'].outcome == AuditOutcome.Error
        assert by_name['Down'].status == 'Connection refused'
        assert by_name['Up'].outcome == AuditOutcome.OK

# ################################################################################################################################
# ################################################################################################################################

class TestHealthProbe:

    def test_every_state_is_recorded_normalized_with_the_raw_one_kept(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        states = [
            ('Exchange Online', 'serviceOperational'),
            ('Microsoft Teams', 'serviceDegradation'),
        ]
        recorded = run_health_probe(audit_log, states, now, cid='health-probe-1')

        assert recorded == 2

        events = _load_events(AuditSource.Microsoft_Health)
        by_name = {event.object_name: event for event in events}

        # The normalized state travels in the status column - healthy means empty
        assert by_name['Exchange Online'].status == ''
        assert by_name['Microsoft Teams'].status == 'degraded'

        # The collector reports only the unhealthy service
        facts = collect_health_facts(engine, now)
        assert len(facts) == 1
        assert facts[0]['object_name'] == 'Microsoft Teams'
        assert facts[0]['health_state'] == 'degraded'

# ################################################################################################################################
# ################################################################################################################################

class TestCanaryProbe:

    def test_a_successful_transfer_writes_an_ok_outcome(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        transfers = []

        def transfer() -> 'None':
            transfers.append(True)

        is_ok = run_canary_probe(audit_log, 'sftp.backups', transfer, now, cid='canary-probe-1')

        assert is_ok is True
        assert transfers == [True]

        events = _load_events(AuditSource.Canary)
        assert len(events) == 1
        assert events[0].event_type == AuditEvent.Canary_Executed
        assert events[0].outcome == AuditOutcome.OK

        facts = collect_canary_facts(engine, now)
        assert facts[0]['canary_failed'] == 0

# ################################################################################################################################

    def test_a_failed_transfer_writes_the_error_the_collector_reads(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        def transfer() -> 'None':
            raise Exception('Upload failed')

        is_ok = run_canary_probe(audit_log, 'sftp.backups', transfer, now, cid='canary-probe-2')

        assert is_ok is False

        events = _load_events(AuditSource.Canary)
        assert len(events) == 1
        assert events[0].outcome == AuditOutcome.Error
        assert events[0].status == 'Upload failed'

        facts = collect_canary_facts(engine, now)
        assert facts[0]['canary_failed'] == 1

# ################################################################################################################################
# ################################################################################################################################
