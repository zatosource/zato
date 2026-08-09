# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting.engine import AlertTransports
from zato.common.alerting.model import AlertAction
from zato.common.alerting.sweep import build_fact_message, read_outcome, run_sweep
from zato.common.api import Alerting, Incidents
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.monitoring.health import EndpointMetrics
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.parser import parse_data_details
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.alerting.sweep import rule_engine_rule_list
    from zato.common.typing_ import anylist, stranydict
    anylist = anylist
    rule_engine_rule_list = rule_engine_rule_list
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-sweep-server'

# The channels the tests seed events and metrics for
_channel_name = 'hl7.sweep.channel'
_other_channel_name = 'hl7.sweep.other'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# ################################################################################################################################
# ################################################################################################################################

# The ruleset the sweep tests match through - one incident rule with its config in the
# outcome keys and one email rule, both written the way the builder writes them.
_rules_text = """
rule
    test_incident_on_errors
docs
    A channel erroring on at least half its traffic is diagnosed as an incident.
when
    alert.source is 'mllp-channel' and
    alert.error_rate is at least 0.5
then
    outcome.action = 'incident'
    outcome.llm_conn = 'default.llm'

rule
    test_email_on_silence
docs
    A feed silent for ten minutes raises an email alert.
when
    alert.silent_seconds is at least 600
then
    outcome.action = 'email'
    outcome.severity = 'critical'
""".strip()

# ################################################################################################################################
# ################################################################################################################################

class _TransportRecorder:
    """ A stand-in for the real transports, remembering everything that went out.
    """
    def __init__(self) -> 'None':
        self.emails:'anylist' = []
        self.invocations:'anylist' = []
        self.publications:'anylist' = []
        self.posts:'anylist' = []

    def make(self) -> 'AlertTransports':
        out = AlertTransports()

        def send_email(addresses:'anylist', subject:'str', body:'str') -> 'None':
            self.emails.append((addresses, subject, body))

        def invoke_service(service:'str', payload:'stranydict') -> 'None':
            self.invocations.append((service, payload))

        def publish(topic:'str', payload:'stranydict') -> 'None':
            self.publications.append((topic, payload))

        def http_post(url:'str', payload:'stranydict') -> 'None':
            self.posts.append((url, payload))

        out.send_email = send_email
        out.invoke_service = invoke_service
        out.publish = publish
        out.http_post = http_post

        return out

# ################################################################################################################################

def _load_rules(text:'str') -> 'rule_engine_rule_list':
    """ Builds runtime rules out of zrules text, the same way a stored version loads.
    """
    documents, errors = parse_data_details(text, Alerting.Ruleset_Name)
    assert errors == []

    loaded = load_documents(documents)

    out = []
    for full_name in loaded.rule_names:
        out.append(loaded.manager[full_name])

    return out

# ################################################################################################################################

def _seed_outcome(audit_log:'AuditLog', cid:'str', outcome:'str', *, object_name:'str'=_channel_name) -> 'None':
    """ Stores one inbound acknowledgment event with the given outcome.
    """
    _ = audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Ack_Sent, object_name, cid=cid, outcome=outcome)

# ################################################################################################################################
# ################################################################################################################################

class TestReadOutcome:

    def test_only_prefixed_targets_come_through_stripped(self) -> 'None':
        then = {
            'outcome.action': 'incident',
            'outcome.llm_conn': 'default.llm',
            'something.else': 'ignored',
        }

        outcome = read_outcome(then)

        assert outcome == {'action': 'incident', 'llm_conn': 'default.llm'}

# ################################################################################################################################
# ################################################################################################################################

class TestBuildFactMessage:

    def test_only_the_measures_that_were_taken_speak(self) -> 'None':
        fact = {
            'source': AuditSource.MLLP_Channel,
            'object_name': _channel_name,
            'error_rate': 0.75,
            'error_count': 3,
            'total_count': 4,
            'window_seconds': 300,
            'outstanding': 0,
            'oldest_waiting_seconds': 0,
            'silent_seconds': 0,
        }

        message = build_fact_message('test_incident_on_errors', fact)

        assert 'error rate 75% (3 of 4 over 300s)' in message
        assert _channel_name in message
        assert 'outstanding' not in message
        assert 'silent' not in message

# ################################################################################################################################
# ################################################################################################################################

class TestRunSweep:

    def test_a_matching_fact_dispatches_the_incident_with_the_outcome_config(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        # Both outcomes are errors - a 100% error rate
        _seed_outcome(audit_log, 'sweep-run-1', AuditOutcome.Error)
        _seed_outcome(audit_log, 'sweep-run-2', AuditOutcome.Error)

        rules = _load_rules(_rules_text)

        result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-sweep-1', now)

        assert result.rule_count == 2
        assert result.fact_count == 1
        assert result.finding_count == 1
        assert result.raised_count == 1
        assert result.deduplicated_count == 0
        assert result.dispatched == [('test_incident_on_errors', AlertAction.Invoke_Service)]

        # The incident outcome invokes the diagnosis service with the remaining
        # outcome keys travelling as the action config
        assert len(recorder.invocations) == 1

        service, payload = recorder.invocations[0]
        assert service == Incidents.Service_Diagnose
        assert payload['object_name'] == _channel_name
        assert payload['source'] == AuditSource.MLLP_Channel
        assert payload['action_config']['llm_conn'] == 'default.llm'
        assert 'error rate 100% (2 of 2' in payload['message']

# ################################################################################################################################

    def test_a_repeated_match_deduplicates_instead_of_raising_anew(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        _seed_outcome(audit_log, 'sweep-dedup-1', AuditOutcome.Error)

        rules = _load_rules(_rules_text)

        # The first sweep raises and dispatches ..
        result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-dedup-1', now)

        assert result.raised_count == 1
        assert len(recorder.invocations) == 1

        # .. and the second one, still inside the dedup window, only counts.
        result_2 = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-dedup-2', now)

        assert result_2.raised_count == 0
        assert result_2.deduplicated_count == 1
        assert result_2.dispatched == []
        assert len(recorder.invocations) == 1

# ################################################################################################################################

    def test_a_fact_below_the_threshold_matches_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        # One of four outcomes is an error - a 25% error rate, below the rule's half
        _seed_outcome(audit_log, 'sweep-low-1', AuditOutcome.Error)
        _seed_outcome(audit_log, 'sweep-low-2', AuditOutcome.OK)
        _seed_outcome(audit_log, 'sweep-low-3', AuditOutcome.OK)
        _seed_outcome(audit_log, 'sweep-low-4', AuditOutcome.OK)

        rules = _load_rules(_rules_text)

        result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-low-1', now)

        assert result.fact_count == 1
        assert result.finding_count == 0
        assert result.dispatched == []
        assert recorder.invocations == []
        assert recorder.emails == []

# ################################################################################################################################

    def test_a_deactivated_rule_matches_nothing_while_remaining_stored(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        _seed_outcome(audit_log, 'sweep-off-1', AuditOutcome.Error)

        rules = _load_rules(_rules_text)

        # The listing screen writes the flag into the rule's own document
        for rule in rules:
            if rule.name == 'test_incident_on_errors':
                rule.document['is_active'] = False

        result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-off-1', now)

        assert result.rule_count == 1
        assert result.finding_count == 0
        assert recorder.invocations == []

# ################################################################################################################################

    def test_each_fact_runs_through_each_rule(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        # One channel errors while another sits silent - two facts, two different rules fire
        _seed_outcome(audit_log, 'sweep-both-1', AuditOutcome.Error)

        metrics = EndpointMetrics()
        metrics.silence_seconds = 1200.0
        metrics_by_name = {_other_channel_name: metrics}

        rules = _load_rules(_rules_text)

        result = run_sweep(
            engine, rules, metrics_by_name, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-both-1', now,
            default_email=_addresses)

        assert result.fact_count == 2
        assert result.raised_count == 2
        assert sorted(result.dispatched) == [
            ('test_email_on_silence', AlertAction.Email_Digest),
            ('test_incident_on_errors', AlertAction.Invoke_Service),
        ]

        # The email rule went out through the email transport with the default addresses
        assert len(recorder.emails) == 1
        assert recorder.emails[0][0] == _addresses

        # The incident rule went out through the service transport
        assert len(recorder.invocations) == 1
        assert recorder.invocations[0][1]['object_name'] == _channel_name

# ################################################################################################################################
# ################################################################################################################################
