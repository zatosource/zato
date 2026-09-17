# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The sweep over the outgoing MLLP ruleset - the negative acknowledgments a connection was answered are matched
# against the codes in force for it, the rule's default or the connection's own, the messages no acknowledgment came
# back for are the connection failures with a window of their own, a connection with alerts off is skipped, and the
# channel rulesets never say a word about an outgoing connection.

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.engine import AlertDefaults, AlertTransports
from zato.common.alerting.object_config import alert_type_mllp_outgoing, get_defaults as get_object_defaults, \
    LLM_Connection_Config_Key
from zato.common.alerting.seed.rules_mllp import mllp_channel_rules, mllp_outgoing_rules
from zato.common.alerting.sweep import run_sweep
from zato.common.api import Alerting
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, AuditSource
from zato.common.hl7.audit import audit_ack_received, audit_message_sent, ACKStatus
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.parser import parse_data_details
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.alerting.sweep import rule_engine_rule_list, SweepResult
    from zato.common.typing_ import any_, anydict, anylist, stranydict
    any_ = any_
    anydict = anydict
    anylist = anylist
    datetime = datetime
    Engine = Engine
    rule_engine_rule_list = rule_engine_rule_list
    stranydict = stranydict
    SweepResult = SweepResult

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-sweep-mllp-outgoing-server'

# The ruleset the connections are judged by and the channel one that must not judge them
_ruleset_name = 'alerts_mllp_outgoing'
_channel_ruleset_name = 'alerts_mllp_channel'

# The outgoing connection with settings of its own and the one without any
_conn_name = 'lab.results'
_other_conn_name = 'adt.outbound'

# The remote system the connections send to
_address = 'lab.example.com:2575'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# The connection the settings route the explanations through
_llm_name = 'ops.llm'

# The message the sent rows carry as their body and what a remote system says when it rejects one
_message_text = 'MSH|^~\\&|ZATO|ZATO|LAB|LAB_SYSTEM|20260914||ORU^R01|MSG-1|P|2.5\rPID|||123'
_reject_text = 'Unknown patient'

# ################################################################################################################################
# ################################################################################################################################

class _TransportRecorder:
    """ A stand-in for the real transports, remembering everything that went out.
    """
    def __init__(self) -> 'None':
        self.emails:'anylist' = []
        self.email_connections:'anylist' = []
        self.invocations:'anylist' = []

    def make(self) -> 'AlertTransports':
        out = AlertTransports()

        def send_email(addresses:'anylist', subject:'str', body:'str', email_connection:'str'='') -> 'None':
            self.emails.append((addresses, subject, body))
            self.email_connections.append(email_connection)

        def invoke_service(service:'str', payload:'stranydict') -> 'None':
            self.invocations.append((service, payload))

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

def _load_rules() -> 'rule_engine_rule_list':
    """ The seeded outgoing MLLP rules and the MLLP channel ones as runtime rules, all of them active - both
    rulesets are loaded so a test can see that only the outgoing one speaks of an outgoing connection.
    """

    # Our response to produce
    out = []

    for ruleset_name, contents in ((_ruleset_name, mllp_outgoing_rules), (_channel_ruleset_name, mllp_channel_rules)):
        documents, errors = parse_data_details(contents, ruleset_name)
        assert errors == []

        loaded = load_documents(documents)

        for full_name in loaded.rule_names:
            out.append(loaded.manager[full_name])

    return out

# ################################################################################################################################

def _seed_message(audit_log:'AuditLog', engine:'Engine', now:'datetime', cid:'str', ack_code:'str', *,
    object_name:'str'=_conn_name, seconds_back:'int'=0, duration_ms:'int'=20) -> 'None':
    """ Stores the message sent and the acknowledgment received, or the timeout marker, that one message of an
    outgoing connection leaves behind, moved back in time if asked to.
    """
    attrs = {'msg_type': 'ORU^R01', 'mrn': '123', 'facility': 'ZATO'}

    message_id = audit_message_sent(audit_log, object_name, _message_text, cid=cid, msg_id=cid, attrs=attrs,
        endpoint=_address)

    if ack_code in (ACKStatus.Timeout, ACKStatus.Application_Accept, ACKStatus.Commit_Accept):
        error_text = ''
    else:
        error_text = _reject_text

    ack_id = audit_ack_received(audit_log, object_name, ack_code, cid=cid, msg_id=cid, duration_ms=duration_ms,
        error_text=error_text)

    if seconds_back:
        event_time_iso = (now - timedelta(seconds=seconds_back)).isoformat()

        statement = update(event_table)
        statement = statement.where(event_table.c.id.in_([message_id, ack_id]))
        statement = statement.values(event_time_iso=event_time_iso)

        with engine.begin() as connection:
            _ = connection.execute(statement)

# ################################################################################################################################

def _seed_failures(audit_log:'AuditLog', engine:'Engine', now:'datetime', prefix:'str', count:'int', ack_code:'str', *,
    object_name:'str'=_conn_name, seconds_back:'int'=0) -> 'None':
    """ Stores the given number of messages a connection had fail with the code - a negative ack or the timeout
    marker - each followed by one it had accepted, so the failures never form an unbroken streak and only the
    rules about counts and rates see them.
    """
    for idx in range(count):
        _seed_message(audit_log, engine, now, f'{prefix}-{idx}-fail', ack_code, object_name=object_name,
            seconds_back=seconds_back)
        _seed_message(audit_log, engine, now, f'{prefix}-{idx}-ok', 'AA', object_name=object_name,
            seconds_back=seconds_back)

# ################################################################################################################################

def _seed_accepted(audit_log:'AuditLog', engine:'Engine', now:'datetime', prefix:'str', count:'int', *,
    object_name:'str'=_conn_name) -> 'None':
    """ Stores the given number of messages a connection had accepted - the traffic that keeps the error rate under its tenth.
    """
    for idx in range(count):
        _seed_message(audit_log, engine, now, f'{prefix}-{idx}', 'AA', object_name=object_name)

# ################################################################################################################################

def _new_object_settings(**values:'any_') -> 'anydict':
    """ The object settings of one outgoing connection at the defaults, with the given values on top.
    The LLM stays out of it unless a test asks for it, so the actions run directly and can be observed.
    """
    settings = get_object_defaults(alert_type_mllp_outgoing)
    settings['use_llm'] = False
    settings.update(values)

    out = {alert_type_mllp_outgoing: {_conn_name: settings}}
    return out

# ################################################################################################################################

def _run_sweep(engine:'Engine', audit_log:'AuditLog', now:'datetime', cid:'str',
    object_settings:'anydict | None') -> 'tuple[SweepResult, _TransportRecorder]':
    """ Runs one sweep of the seeded rulesets with the given object settings.
    """
    defaults = AlertDefaults()
    defaults.email_to = _addresses

    recorder = _TransportRecorder()
    rules = _load_rules()

    result = run_sweep(engine, rules, {}, AuditSource.MLLP_Outgoing, recorder.make(), audit_log, cid, now,
        defaults=defaults, object_settings=object_settings)

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
# ################################################################################################################################

class TestNegativeAcks:

    def test_the_rules_default_codes_count_every_negative_ack(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Two rejects and one application error out of thirty-six messages - under the error rate's tenth,
        # at the default threshold of three negative acks
        _seed_failures(audit_log, engine, now, 'def-ar', 2, 'AR')
        _seed_failures(audit_log, engine, now, 'def-ae', 1, 'AE')
        _seed_accepted(audit_log, engine, now, 'def-ok', 30)

        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-out-default', None)

        assert _rule_names(result) == ['Negative_Acks']
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert '3 negative acknowledgments the connection alerts on' in body
        assert '(AE, AR x2)' in body

# ################################################################################################################################

    def test_the_connections_own_codes_stand_in_for_the_rules_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three application errors and nothing else negative
        _seed_failures(audit_log, engine, now, 'own-ae', 3, 'AE')
        _seed_accepted(audit_log, engine, now, 'own-ok', 30)

        # The default codes count them ..
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-out-own-1', None)
        assert _rule_names(result) == ['Negative_Acks']

        # .. a connection naming the rejects alone does not ..
        object_settings = _new_object_settings(ack_codes='AR')
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-out-own-2', object_settings)
        assert result.raised_count == 0

        # .. and once it names the errors it counts them again.
        object_settings = _new_object_settings(ack_codes='AE')
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-out-own-3', object_settings)
        assert _rule_names(result) == ['Negative_Acks']

        _, _, body = recorder.emails[0]
        assert '(AE x3)' in body

# ################################################################################################################################

    def test_three_rejects_fire_on_a_connection_naming_the_rejects(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 'rej', 3, 'AR')
        _seed_accepted(audit_log, engine, now, 'rej-ok', 30)

        object_settings = _new_object_settings(ack_codes='AR')
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-out-rejects', object_settings)

        assert _rule_names(result) == ['Negative_Acks']

        _, _, body = recorder.emails[0]
        assert '(AR x3)' in body

# ################################################################################################################################

    def test_the_connections_own_threshold_stands_in_for_the_rules_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 'thr', 1, 'AR')
        _seed_accepted(audit_log, engine, now, 'thr-ok', 30)

        # One reject is under the rule's three - nothing without settings ..
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-out-threshold-1', None)
        assert result.raised_count == 0

        # .. and an alert once the connection itself asks for one.
        object_settings = _new_object_settings(ack_threshold=1)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-out-threshold-2', object_settings)

        assert _rule_names(result) == ['Negative_Acks']
        assert len(recorder.emails) == 1

# ################################################################################################################################

    def test_the_acks_window_of_the_connection_applies_to_the_acks_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three rejects half an hour back - outside the rule's five minutes, inside the connection's own hour
        _seed_failures(audit_log, engine, now, 'win', 3, 'AR', seconds_back=1800)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-out-window-1', None)
        assert result.raised_count == 0

        # The error rate, measured over its own five minutes, still sees nothing
        object_settings = _new_object_settings(acks_window=3600)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-out-window-2', object_settings)

        assert _rule_names(result) == ['Negative_Acks']

        _, _, body = recorder.emails[0]
        assert '(AR x3) over 3600s' in body

# ################################################################################################################################

    def test_the_connections_own_llm_connection_rides_in_the_outcome(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 'llm', 3, 'CR')
        _seed_accepted(audit_log, engine, now, 'llm-ok', 30)

        object_settings = _new_object_settings(use_llm=True, llm_connection=_llm_name)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-out-llm', object_settings)

        assert _rule_names(result) == ['Negative_Acks']
        assert recorder.emails == []
        assert len(recorder.invocations) == 1

        service, payload = recorder.invocations[0]
        assert service == Alerting.Service_Explain
        assert payload['source'] == AuditSource.MLLP_Outgoing
        assert payload['object_name'] == _conn_name
        assert payload['action_config'][LLM_Connection_Config_Key] == _llm_name
        assert payload['fact']['ack_count'] == 3
        assert payload['fact']['ack_code_counts'] == {'CR': 3}
        assert payload['thresholds'] == {'ack_codes': 'AE, AR, CE, CR', 'ack_threshold': 3, 'window_seconds': 300}

# ################################################################################################################################
# ################################################################################################################################

class TestConnectionFailures:

    def test_three_timeouts_are_connection_failures_and_not_negative_acks(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 'to', 3, ACKStatus.Timeout)
        _seed_accepted(audit_log, engine, now, 'to-ok', 30)

        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-out-timeouts', None)

        assert _rule_names(result) == ['Connection_Failures']

        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert '3 timeouts or connection failures' in body
        assert 'negative acknowledgments' not in body

# ################################################################################################################################

    def test_the_connections_own_threshold_and_window_apply_to_the_failures(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Two timeouts half an hour back - under the rule's three and outside its five minutes
        _seed_failures(audit_log, engine, now, 'cf', 2, ACKStatus.Timeout, seconds_back=1800)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-out-cf-1', None)
        assert result.raised_count == 0

        # The connection's own hour finds them, its own threshold of two counts them
        object_settings = _new_object_settings(connection_failures=2, connection_failures_window=3600)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-out-cf-2', object_settings)

        assert _rule_names(result) == ['Connection_Failures']

        _, _, body = recorder.emails[0]
        assert '2 timeouts or connection failures over 3600s' in body

# ################################################################################################################################
# ################################################################################################################################

class TestTheOtherRules:

    def test_a_connection_with_alerts_off_is_skipped_while_another_still_raises(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 'off-a', 5, 'AR')
        _seed_failures(audit_log, engine, now, 'off-b', 5, 'AR', object_name=_other_conn_name)

        object_settings = _new_object_settings(is_active=False)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-out-off', object_settings)

        # Five rejects out of ten messages are both too many rejects and too high an error rate - the MLLP
        # channel ruleset, loaded alongside, has nothing to say about either connection
        assert _rule_names(result) == ['Error_Rate', 'Negative_Acks']

        for _, _, body in recorder.emails:
            assert _other_conn_name in body
            assert _conn_name not in body

# ################################################################################################################################

    def test_a_streak_of_failures_is_a_connection_down(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_message(audit_log, engine, now, 'streak-0', 'AA')
        _seed_message(audit_log, engine, now, 'streak-1', ACKStatus.Timeout)
        _seed_message(audit_log, engine, now, 'streak-2', 'AE')
        _seed_message(audit_log, engine, now, 'streak-3', ACKStatus.Timeout)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-out-streak', None)

        assert 'Connection_Down' in _rule_names(result)
        assert 'Channel_Failing' not in _rule_names(result)

# ################################################################################################################################

    def test_slow_acknowledgments_are_slow_responses(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_message(audit_log, engine, now, 'slow-1', 'AA', duration_ms=6000)
        _seed_message(audit_log, engine, now, 'slow-2', 'AA', duration_ms=6000)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-out-slow', None)

        assert _rule_names(result) == ['Slow_Responses']

# ################################################################################################################################
# ################################################################################################################################
