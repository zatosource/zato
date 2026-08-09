# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.incidents.evidence import build_evidence, collect_audit_trail

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under.
_server_name = 'test-incidents-server'

# The connection the tests write events about.
_conn_name = 'CRM API'

# ################################################################################################################################
# ################################################################################################################################

def _write_events() -> 'None':
    """ One successful exchange and one failed one, oldest first.
    """
    audit_log = AuditLog(_server_name)

    _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _conn_name,
        cid='cid-ok', endpoint='POST https://crm.example.com/api', outcome=AuditOutcome.OK,
        data='{"customer": "abc"}')

    _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, _conn_name,
        cid='cid-ok', endpoint='POST https://crm.example.com/api', outcome=AuditOutcome.OK,
        status='200', data='{"result": "created"}')

    _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _conn_name,
        cid='cid-error', endpoint='POST https://crm.example.com/api', outcome=AuditOutcome.OK,
        data='{"customer": "def"}')

    _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, _conn_name,
        cid='cid-error', endpoint='POST https://crm.example.com/api', outcome=AuditOutcome.Error,
        status='503', data='Service unavailable')

# ################################################################################################################################
# ################################################################################################################################

class TestCollectAuditTrail:

    def test_the_trail_is_newest_first(self) -> 'None':
        _write_events()
        engine = get_audit_engine()

        trail = collect_audit_trail(engine, AuditSource.REST_Outgoing, _conn_name, 20)

        assert len(trail) == 4
        assert trail[0]['cid'] == 'cid-error'
        assert trail[0]['event_type'] == AuditEvent.Response_Received
        assert trail[-1]['cid'] == 'cid-ok'
        assert trail[-1]['event_type'] == AuditEvent.Request_Sent

    def test_only_failed_events_carry_their_data(self) -> 'None':
        _write_events()
        engine = get_audit_engine()

        trail = collect_audit_trail(engine, AuditSource.REST_Outgoing, _conn_name, 20)

        failed = trail[0]
        successful = trail[1]

        assert failed['outcome'] == AuditOutcome.Error
        assert failed['data'] == 'Service unavailable'

        assert successful['outcome'] == AuditOutcome.OK
        assert 'data' not in successful

    def test_the_trail_respects_the_event_limit(self) -> 'None':
        _write_events()
        engine = get_audit_engine()

        trail = collect_audit_trail(engine, AuditSource.REST_Outgoing, _conn_name, 2)

        assert len(trail) == 2
        assert trail[0]['cid'] == 'cid-error'

    def test_other_connections_never_appear_in_the_trail(self) -> 'None':
        _write_events()
        engine = get_audit_engine()

        trail = collect_audit_trail(engine, AuditSource.REST_Outgoing, 'Billing API', 20)

        assert trail == []

# ################################################################################################################################
# ################################################################################################################################

class TestBuildEvidence:

    def test_only_the_keys_of_interest_go_into_the_pack(self) -> 'None':

        conn_config = {
            'name': _conn_name,
            'address_host': 'https://crm.example.com',
            'address_url_path': '/api',
            'timeout': 10,
            'password': 'test-password',
            'sec_type': 'basic_auth',
            'security_name': 'CRM Credentials',
        }

        alert = {'rule': 'crm-errors', 'kind': 'error-rate', 'message': 'Test alert', 'severity': 'warning', 'count': 1}

        evidence = build_evidence(alert, conn_config, [])

        assert evidence['alert'] == alert
        assert evidence['audit_trail'] == []

        connection = evidence['connection']

        assert connection['name'] == _conn_name
        assert connection['address_host'] == 'https://crm.example.com'
        assert connection['security_name'] == 'CRM Credentials'

        # Credentials never enter an evidence pack.
        assert 'password' not in connection

    def test_keys_the_config_does_not_have_are_left_out(self) -> 'None':

        conn_config = {'name': _conn_name, 'timeout': 10}
        alert = {'rule': 'crm-errors', 'kind': 'error-rate', 'message': 'Test alert', 'severity': 'warning', 'count': 1}

        evidence = build_evidence(alert, conn_config, [])

        assert evidence['connection'] == {'name': _conn_name, 'timeout': 10}

# ################################################################################################################################
# ################################################################################################################################
