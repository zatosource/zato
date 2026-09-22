# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue delivery alerts of outgoing connections - the collector turns the delivery page's rows into one fact per
# connection under the audit source of its kind, the DLQ rule fires off one message with no audit rows at all and
# stays open while the depth holds, the backlog rule fires at a thousand and stays quiet under it, a connection's
# own thresholds stand in for the rules' defaults, the four rulesets each match their own source alone, the
# vocabulary speaks the two depths and the fact message words them.

# Zato
from zato.common.alerting.collectors import collect_facts, collect_queue_facts, new_fact
from zato.common.alerting.engine import AlertDefaults, AlertTransports
from zato.common.alerting.fact_message import build_fact_message
from zato.common.alerting.object_config import alert_type_fhir, alert_type_mllp_outgoing, alert_type_rest, alert_type_soap, \
    get_defaults as get_object_defaults, get_field_names
from zato.common.alerting.seed.api import alerting_vocabulary
from zato.common.alerting.seed.rules_connections import rest_rules, soap_rules
from zato.common.alerting.seed.rules_fhir import fhir_rules
from zato.common.alerting.seed.rules_mllp import mllp_outgoing_rules
from zato.common.alerting.seed.rules_queue import DLQ_Messages_Rule, DLQ_Threshold_Value, Queue_Backlog_Rule, \
    Queue_Depth_Threshold_Value
from zato.common.alerting.sweep import run_sweep
from zato.common.audit_log.api import get_audit_engine, AuditLog, AuditSource
from zato.common.pubsub.outgoing import OutgoingType
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.parser import parse_data_details
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.alerting.sweep import rule_engine_rule_list, SweepResult
    from zato.common.typing_ import any_, anydict, anylist, dictlist, stranydict
    any_ = any_
    anydict = anydict
    anylist = anylist
    dictlist = dictlist
    rule_engine_rule_list = rule_engine_rule_list
    stranydict = stranydict
    SweepResult = SweepResult

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-sweep-queues-server'

# The connections under test - one of each kind that can use a queue
_rest_name = 'billing.rest'
_soap_name = 'billing.soap'
_fhir_name = 'records.fhir'
_mllp_name = 'lab.mllp'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# Each kind's ruleset, its rules text, the type its settings are stored under and the source its facts carry
_kinds = {
    OutgoingType.REST: ('alerts_rest', rest_rules, alert_type_rest, AuditSource.REST_Outgoing, _rest_name),
    OutgoingType.SOAP: ('alerts_soap', soap_rules, alert_type_soap, AuditSource.SOAP_Outgoing, _soap_name),
    OutgoingType.FHIR: ('alerts_fhir', fhir_rules, alert_type_fhir, AuditSource.FHIR, _fhir_name),
    OutgoingType.MLLP: ('alerts_mllp_outgoing', mllp_outgoing_rules, alert_type_mllp_outgoing, AuditSource.MLLP_Outgoing,
        _mllp_name),
}

# ################################################################################################################################
# ################################################################################################################################

class _TransportRecorder:
    """ A stand-in for the real transports, remembering everything that went out.
    """
    def __init__(self) -> 'None':
        self.emails:'anylist' = []

    def make(self) -> 'AlertTransports':
        out = AlertTransports()

        def send_email(addresses:'anylist', subject:'str', body:'str', email_connection:'str'='') -> 'None':
            self.emails.append((addresses, subject, body))

        def invoke_service(service:'str', payload:'stranydict') -> 'None':
            pass

        def publish(topic:'str', payload:'stranydict') -> 'None':
            pass

        def http_post(url:'str', payload:'stranydict') -> 'None':
            pass

        out.send_email = send_email
        out.invoke_service = invoke_service
        out.publish = publish
        out.http_post = http_post

        return out

# ################################################################################################################################

def _row(conn_type:'str', name:'str', *, queue_depth:'int'=0, dlq_depth:'int'=0) -> 'anydict':
    """ One row the way the delivery page lists it.
    """
    out = {
        'conn_type': conn_type,
        'conn_id': 1,
        'name': name,
        'queue_depth': queue_depth,
        'dlq_depth': dlq_depth,
    }
    return out

# ################################################################################################################################

def _load_rules(conn_type:'str') -> 'rule_engine_rule_list':
    """ The seeded rules of one kind's ruleset as runtime rules, all of them active.
    """
    ruleset_name, rules_text, _, _, _ = _kinds[conn_type]

    documents, errors = parse_data_details(rules_text, ruleset_name)
    assert errors == []

    loaded = load_documents(documents)

    # Our response to produce
    out = []

    for full_name in loaded.rule_names:
        out.append(loaded.manager[full_name])

    return out

# ################################################################################################################################

def _new_object_settings(conn_type:'str', **values:'any_') -> 'anydict':
    """ The object settings of one kind's connection at the defaults, with the given values on top.
    The explaining LLM stays out of it, so the actions run directly and can be observed.
    """
    _, _, alert_type, _, name = _kinds[conn_type]

    settings = get_object_defaults(alert_type)
    settings['use_llm'] = False
    settings.update(values)

    out = {alert_type: {name: settings}}
    return out

# ################################################################################################################################

def _run_sweep(conn_type:'str', queue_rows:'dictlist', cid:'str', object_settings:'anydict | None'=None,
    ) -> 'tuple[SweepResult, _TransportRecorder]':
    """ Runs one sweep of one kind's ruleset over the given queue rows, with no audit rows at all.
    """
    audit_log = AuditLog(_server_name)
    engine = get_audit_engine()
    now = utcnow()

    defaults = AlertDefaults()
    defaults.email_to = _addresses

    recorder = _TransportRecorder()
    rules = _load_rules(conn_type)

    if object_settings is None:
        object_settings = _new_object_settings(conn_type)

    result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, cid, now,
        defaults=defaults, object_settings=object_settings, queue_rows=queue_rows)

    return result, recorder

# ################################################################################################################################

def _rule_names(result:'SweepResult') -> 'list':
    """ The names of the rules that dispatched an action, in order.
    """
    out = []
    for rule_name, _ in result.dispatched:
        out.append(rule_name)

    return out

# ################################################################################################################################

def _fact_of(facts:'dictlist', object_name:'str') -> 'anydict':
    """ The one fact of the given object.
    """
    for fact in facts:
        if fact['object_name'] == object_name:
            return fact

    raise AssertionError(f'No fact of {object_name} in {facts}')

# ################################################################################################################################
# ################################################################################################################################

class TestCollector:

    def test_each_row_is_one_fact_under_the_source_of_its_kind(self) -> 'None':
        rows = [
            _row(OutgoingType.MLLP, _mllp_name, queue_depth=4, dlq_depth=1),
            _row(OutgoingType.REST, _rest_name, queue_depth=12, dlq_depth=0),
            _row(OutgoingType.SOAP, _soap_name, queue_depth=0, dlq_depth=3),
            _row(OutgoingType.FHIR, _fhir_name, queue_depth=7, dlq_depth=2),
        ]

        facts = collect_queue_facts(rows)
        assert len(facts) == 4

        rest_fact = _fact_of(facts, _rest_name)
        assert rest_fact['source'] == AuditSource.REST_Outgoing
        assert rest_fact['queue_depth'] == 12
        assert rest_fact['dlq_depth'] == 0

        assert _fact_of(facts, _soap_name)['source'] == AuditSource.SOAP_Outgoing
        assert _fact_of(facts, _soap_name)['dlq_depth'] == 3

        assert _fact_of(facts, _fhir_name)['source'] == AuditSource.FHIR
        assert _fact_of(facts, _fhir_name)['queue_depth'] == 7

        assert _fact_of(facts, _mllp_name)['source'] == AuditSource.MLLP_Outgoing
        assert _fact_of(facts, _mllp_name)['dlq_depth'] == 1

        # The facts are in a stable order - by kind, then by name
        assert [fact['object_name'] for fact in facts] == [_fhir_name, _mllp_name, _rest_name, _soap_name]

        # Every other measure rests at zero - a depth has no window
        assert rest_fact['window_seconds'] == 0
        assert rest_fact['error_count'] == 0

# ################################################################################################################################

    def test_a_kind_without_an_alert_type_is_left_out_and_no_rows_are_no_facts(self) -> 'None':
        rows = [
            _row(OutgoingType.SFTP, 'archive.sftp', queue_depth=9, dlq_depth=9),
            _row(OutgoingType.REST, _rest_name, queue_depth=1),
        ]

        facts = collect_queue_facts(rows)
        assert [fact['object_name'] for fact in facts] == [_rest_name]

        assert collect_queue_facts([]) == []
        assert collect_queue_facts(None) == []

# ################################################################################################################################

    def test_the_depths_reach_the_merged_facts(self) -> 'None':
        engine = get_audit_engine()
        now = utcnow()

        rows = [_row(OutgoingType.REST, _rest_name, queue_depth=1500, dlq_depth=2)]
        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, queue_rows=rows)

        fact = _fact_of(facts, _rest_name)
        assert fact['source'] == AuditSource.REST_Outgoing
        assert fact['queue_depth'] == 1500
        assert fact['dlq_depth'] == 2

        # Without rows there is nothing about the connection
        assert collect_facts(engine, {}, AuditSource.MLLP_Channel, now) == []

# ################################################################################################################################
# ################################################################################################################################

class TestRules:

    def test_one_message_in_the_dlq_fires_with_no_audit_rows_at_all(self) -> 'None':

        for conn_type in _kinds:
            _, _, _, _, name = _kinds[conn_type]

            rows = [_row(conn_type, name, dlq_depth=1)]
            result, recorder = _run_sweep(conn_type, rows, f'cid-dlq-{conn_type}')

            assert _rule_names(result) == [DLQ_Messages_Rule], conn_type
            assert len(recorder.emails) == 1, conn_type

            _, _, body = recorder.emails[0]
            assert name in body
            assert '1 message in the DLQ' in body

# ################################################################################################################################

    def test_an_empty_dlq_and_a_shallow_queue_stay_quiet(self) -> 'None':

        for conn_type in _kinds:
            _, _, _, _, name = _kinds[conn_type]

            rows = [_row(conn_type, name, queue_depth=Queue_Depth_Threshold_Value - 1, dlq_depth=DLQ_Threshold_Value - 1)]
            result, _ = _run_sweep(conn_type, rows, f'cid-quiet-{conn_type}')

            assert result.raised_count == 0, conn_type

# ################################################################################################################################

    def test_the_dlq_alert_stays_open_while_the_depth_holds(self) -> 'None':

        rows = [_row(OutgoingType.REST, _rest_name, dlq_depth=1)]

        # Each sweep is its own match - the dedup window is the engine's business and the rule keeps matching
        result, _ = _run_sweep(OutgoingType.REST, rows, 'cid-dlq-open-1')
        assert _rule_names(result) == [DLQ_Messages_Rule]

        result, _ = _run_sweep(OutgoingType.REST, rows, 'cid-dlq-open-2')
        assert _rule_names(result) == [DLQ_Messages_Rule]

        # Once the DLQ is emptied there is nothing left to say
        rows = [_row(OutgoingType.REST, _rest_name, dlq_depth=0)]
        result, _ = _run_sweep(OutgoingType.REST, rows, 'cid-dlq-open-3')
        assert result.raised_count == 0

# ################################################################################################################################

    def test_a_thousand_waiting_messages_fire_the_backlog_as_a_warning(self) -> 'None':

        rows = [_row(OutgoingType.SOAP, _soap_name, queue_depth=Queue_Depth_Threshold_Value)]
        result, recorder = _run_sweep(OutgoingType.SOAP, rows, 'cid-backlog-1')

        assert _rule_names(result) == [Queue_Backlog_Rule]

        _, _, body = recorder.emails[0]
        assert '1,000 messages in the queue' in body

        # The backlog is a warning and the DLQ an error, in every kind's ruleset
        for conn_type in _kinds:
            severities = {}

            for rule in _load_rules(conn_type):
                for then in rule.document['then']:
                    if then['target'] == 'outcome.severity':
                        severities[rule.name] = then['value']['value']

            assert severities[Queue_Backlog_Rule] == 'warning', conn_type
            assert severities[DLQ_Messages_Rule] == 'error', conn_type

# ################################################################################################################################

    def test_both_rules_fire_off_one_connection_with_both_depths(self) -> 'None':

        rows = [_row(OutgoingType.FHIR, _fhir_name, queue_depth=1204, dlq_depth=5)]
        result, recorder = _run_sweep(OutgoingType.FHIR, rows, 'cid-both-1')

        assert sorted(_rule_names(result)) == [DLQ_Messages_Rule, Queue_Backlog_Rule]
        assert len(recorder.emails) == 2

        for _, _, body in recorder.emails:
            assert '5 messages in the DLQ' in body
            assert '1,204 messages in the queue' in body

# ################################################################################################################################

    def test_the_connections_own_thresholds_stand_in_for_the_rules_defaults(self) -> 'None':

        rows = [_row(OutgoingType.MLLP, _mllp_name, queue_depth=40, dlq_depth=2)]

        # At the defaults the DLQ fires and the backlog does not ..
        result, _ = _run_sweep(OutgoingType.MLLP, rows, 'cid-own-1')
        assert _rule_names(result) == [DLQ_Messages_Rule]

        # .. under the connection's own three in the DLQ and thirty in the queue it is the other way around
        object_settings = _new_object_settings(OutgoingType.MLLP, dlq_messages=3, queue_depth=30)
        result, _ = _run_sweep(OutgoingType.MLLP, rows, 'cid-own-2', object_settings)
        assert _rule_names(result) == [Queue_Backlog_Rule]

# ################################################################################################################################

    def test_a_connection_with_alerts_off_raises_nothing(self) -> 'None':

        rows = [_row(OutgoingType.REST, _rest_name, queue_depth=5000, dlq_depth=50)]

        object_settings = _new_object_settings(OutgoingType.REST, is_active=False)
        result, _ = _run_sweep(OutgoingType.REST, rows, 'cid-off-1', object_settings)

        assert result.raised_count == 0

# ################################################################################################################################

    def test_each_ruleset_reads_its_own_source_alone(self) -> 'None':

        for conn_type in _kinds:
            _, _, _, own_source, _ = _kinds[conn_type]

            for rule in _load_rules(conn_type):

                if rule.name not in (DLQ_Messages_Rule, Queue_Backlog_Rule):
                    continue

                # A connection of every other kind, deep in both, is not this ruleset's business
                for other_type in _kinds:
                    _, _, _, other_source, other_name = _kinds[other_type]

                    fact = new_fact(other_source, other_name)
                    fact['queue_depth'] = 100000
                    fact['dlq_depth'] = 100000

                    is_match = bool(rule.match({'alert': fact}))
                    assert is_match is (other_source == own_source), (conn_type, rule.name, other_source)

# ################################################################################################################################
# ################################################################################################################################

class TestSeedAndWording:

    def test_the_vocabulary_speaks_the_two_depths(self) -> 'None':
        vocabulary = alerting_vocabulary()

        phrases = {}
        for entity in vocabulary['entities']:
            for attribute in entity['attributes']:
                phrases[attribute['name']] = attribute['phrase']

        assert 'queue' in phrases['queue_depth']
        assert 'DLQ' in phrases['dlq_depth']

# ################################################################################################################################

    def test_the_four_types_carry_the_two_fields_and_nobody_else_does(self) -> 'None':

        for alert_type in (alert_type_rest, alert_type_soap, alert_type_fhir, alert_type_mllp_outgoing):
            names = get_field_names(alert_type)
            assert 'dlq_messages' in names, alert_type
            assert 'queue_depth' in names, alert_type

            defaults = get_object_defaults(alert_type)
            assert defaults['dlq_messages'] == DLQ_Threshold_Value, alert_type
            assert defaults['queue_depth'] == Queue_Depth_Threshold_Value, alert_type

        for alert_type in ('llm', 'mcp', 'channels', 'mllp_channel', 'sql', 'file_transfer'):
            names = get_field_names(alert_type)
            assert 'dlq_messages' not in names, alert_type
            assert 'queue_depth' not in names, alert_type

# ################################################################################################################################

    def test_the_fact_message_words_the_depths(self) -> 'None':

        fact = new_fact(AuditSource.REST_Outgoing, _rest_name)
        fact['dlq_depth'] = 1
        fact['queue_depth'] = 1204

        message = build_fact_message(DLQ_Messages_Rule, fact)

        assert '1 message in the DLQ' in message
        assert '1,204 messages in the queue' in message

        # A depth of zero is not worth a word
        fact = new_fact(AuditSource.REST_Outgoing, _rest_name)
        fact['dlq_depth'] = 2

        message = build_fact_message(DLQ_Messages_Rule, fact)

        assert '2 messages in the DLQ' in message
        assert 'in the queue' not in message

# ################################################################################################################################
# ################################################################################################################################
