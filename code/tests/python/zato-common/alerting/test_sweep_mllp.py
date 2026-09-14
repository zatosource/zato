# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The sweep over the MLLP channel ruleset - the negative acknowledgments a channel sent are matched against the
# codes in force for it, the rule's default or the channel's own, the acks window of the channel applies to that
# count alone, a channel with alerts off is skipped, and the silence of a channel expecting traffic is measured
# off its newest message received while the HTTP channel ruleset never says a word about it.

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.engine import AlertDefaults, AlertTransports
from zato.common.alerting.object_config import alert_type_mllp_channel, get_defaults as get_object_defaults, \
    LLM_Connection_Config_Key
from zato.common.alerting.seed.rules_common import channels_rules
from zato.common.alerting.seed.rules_mllp import mllp_channel_rules
from zato.common.alerting.sweep import run_sweep
from zato.common.api import Alerting
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, AuditSource
from zato.common.hl7.audit import audit_ack_sent, audit_message_received
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
_server_name = 'test-sweep-mllp-server'

# The ruleset the channels are judged by and the HTTP one that must not judge them
_ruleset_name = 'alerts_mllp_channel'
_channels_ruleset_name = 'alerts_channels'

# The MLLP channel with settings of its own and the one without any
_channel_name = 'adt.intake'
_other_channel_name = 'orm.intake'

# The sending facility of the messages
_facility = 'GENERAL_HOSPITAL'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# The connection the settings route the explanations through
_llm_name = 'ops.llm'

# The message and the ack the rows carry as their bodies
_message_text = 'MSH|^~\\&|ADT|GENERAL_HOSPITAL|ZATO|ZATO|20260914||ADT^A01|MSG-1|P|2.5\rPID|||123'
_ack_text = 'MSH|^~\\&|ZATO|ZATO|ADT|GENERAL_HOSPITAL|20260914||ACK^A01|ACK-1|P|2.5\rMSA|{code}|MSG-1'

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
    """ The seeded MLLP channel rules and the HTTP channel ones as runtime rules, all of them active - both
    rulesets are loaded so a test can see that only the MLLP one speaks of an MLLP channel.
    """

    # Our response to produce
    out = []

    for ruleset_name, contents in ((_ruleset_name, mllp_channel_rules), (_channels_ruleset_name, channels_rules)):
        documents, errors = parse_data_details(contents, ruleset_name)
        assert errors == []

        loaded = load_documents(documents)

        for full_name in loaded.rule_names:
            out.append(loaded.manager[full_name])

    return out

# ################################################################################################################################

def _seed_message(audit_log:'AuditLog', engine:'Engine', now:'datetime', cid:'str', ack_code:'str', *,
    object_name:'str'=_channel_name, seconds_back:'int'=0, duration_ms:'int'=20) -> 'None':
    """ Stores the message received and the acknowledgment sent that one message of a channel leaves behind,
    moved back in time if asked to.
    """
    attrs = {'msg_type': 'ADT^A01', 'mrn': '123', 'facility': _facility, 'ack_status': ''}

    message_id = audit_message_received(audit_log, object_name, _message_text, cid=cid, msg_id=cid, attrs=attrs)

    ack_id = audit_ack_sent(audit_log, object_name, ack_code, _ack_text.format(code=ack_code), cid=cid, msg_id=cid,
        facility=_facility, duration_ms=duration_ms)

    if seconds_back:
        event_time_iso = (now - timedelta(seconds=seconds_back)).isoformat()

        statement = update(event_table)
        statement = statement.where(event_table.c.id.in_([message_id, ack_id]))
        statement = statement.values(event_time_iso=event_time_iso)

        with engine.begin() as connection:
            _ = connection.execute(statement)

# ################################################################################################################################

def _seed_negative_acks(audit_log:'AuditLog', engine:'Engine', now:'datetime', prefix:'str', count:'int', ack_code:'str', *,
    object_name:'str'=_channel_name, seconds_back:'int'=0) -> 'None':
    """ Stores the given number of messages a channel acknowledged negatively with the code, each followed by one
    it accepted, so the failures never form an unbroken streak and only the rules about counts and rates see them.
    """
    for idx in range(count):
        _seed_message(audit_log, engine, now, f'{prefix}-{idx}-nack', ack_code, object_name=object_name,
            seconds_back=seconds_back)
        _seed_message(audit_log, engine, now, f'{prefix}-{idx}-ok', 'AA', object_name=object_name,
            seconds_back=seconds_back)

# ################################################################################################################################

def _seed_accepted(audit_log:'AuditLog', engine:'Engine', now:'datetime', prefix:'str', count:'int', *,
    object_name:'str'=_channel_name) -> 'None':
    """ Stores the given number of messages a channel accepted - the traffic that keeps the error rate under its tenth.
    """
    for idx in range(count):
        _seed_message(audit_log, engine, now, f'{prefix}-{idx}', 'AA', object_name=object_name)

# ################################################################################################################################

def _new_object_settings(**values:'any_') -> 'anydict':
    """ The object settings of one MLLP channel at the defaults, with the given values on top.
    The LLM stays out of it unless a test asks for it, so the actions run directly and can be observed.
    """
    settings = get_object_defaults(alert_type_mllp_channel)
    settings['use_llm'] = False
    settings.update(values)

    out = {alert_type_mllp_channel: {_channel_name: settings}}
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

    result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, cid, now,
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
        _seed_negative_acks(audit_log, engine, now, 'def-ar', 2, 'AR')
        _seed_negative_acks(audit_log, engine, now, 'def-ae', 1, 'AE')
        _seed_accepted(audit_log, engine, now, 'def-ok', 30)

        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-default', None)

        assert _rule_names(result) == ['Negative_Acks']
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _channel_name in body
        assert '(MLLP channel)' in body
        assert '3 negative acknowledgments the channel alerts on' in body
        assert '(AE, AR x2)' in body

# ################################################################################################################################

    def test_the_channels_own_codes_stand_in_for_the_rules_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three application errors and nothing else negative
        _seed_negative_acks(audit_log, engine, now, 'own-ae', 3, 'AE')
        _seed_accepted(audit_log, engine, now, 'own-ok', 30)

        # The default codes count them ..
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-own-1', None)
        assert _rule_names(result) == ['Negative_Acks']

        # .. a channel naming the rejects alone does not ..
        object_settings = _new_object_settings(ack_codes='AR, CR')
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-own-2', object_settings)
        assert result.raised_count == 0

        # .. and once it names the errors it counts them again.
        object_settings = _new_object_settings(ack_codes='AE')
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-own-3', object_settings)
        assert _rule_names(result) == ['Negative_Acks']

        _, _, body = recorder.emails[0]
        assert '(AE x3)' in body

# ################################################################################################################################

    def test_the_channels_own_threshold_stands_in_for_the_rules_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_negative_acks(audit_log, engine, now, 'thr', 1, 'AR')
        _seed_accepted(audit_log, engine, now, 'thr-ok', 30)

        # One reject is under the rule's three - nothing without settings ..
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-threshold-1', None)
        assert result.raised_count == 0

        # .. and an alert once the channel itself asks for one.
        object_settings = _new_object_settings(ack_threshold=1)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-threshold-2', object_settings)

        assert _rule_names(result) == ['Negative_Acks']
        assert len(recorder.emails) == 1

# ################################################################################################################################

    def test_the_acks_window_of_the_channel_applies_to_the_acks_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three rejects half an hour back - outside the rule's five minutes, inside the channel's own hour
        _seed_negative_acks(audit_log, engine, now, 'win', 3, 'AR', seconds_back=1800)

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-window-1', None)
        assert result.raised_count == 0

        # The error rate, measured over its own five minutes, still sees nothing
        object_settings = _new_object_settings(acks_window=3600)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-window-2', object_settings)

        assert _rule_names(result) == ['Negative_Acks']

        _, _, body = recorder.emails[0]
        assert '(AR x3) over 3600s' in body

# ################################################################################################################################

    def test_the_channels_own_llm_connection_rides_in_the_outcome(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_negative_acks(audit_log, engine, now, 'llm', 3, 'CR')
        _seed_accepted(audit_log, engine, now, 'llm-ok', 30)

        object_settings = _new_object_settings(use_llm=True, llm_connection=_llm_name)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-llm', object_settings)

        assert _rule_names(result) == ['Negative_Acks']
        assert recorder.emails == []
        assert len(recorder.invocations) == 1

        service, payload = recorder.invocations[0]
        assert service == Alerting.Service_Explain
        assert payload['source'] == AuditSource.MLLP_Channel
        assert payload['object_name'] == _channel_name
        assert payload['action_config'][LLM_Connection_Config_Key] == _llm_name
        assert payload['fact']['ack_count'] == 3
        assert payload['fact']['ack_code_counts'] == {'CR': 3}
        assert payload['thresholds'] == {'ack_codes': 'AE, AR, CE, CR', 'ack_threshold': 3, 'window_seconds': 300}

# ################################################################################################################################
# ################################################################################################################################

class TestTheOtherRules:

    def test_a_channel_with_alerts_off_is_skipped_while_another_still_raises(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_negative_acks(audit_log, engine, now, 'off-a', 5, 'AR')
        _seed_negative_acks(audit_log, engine, now, 'off-b', 5, 'AR', object_name=_other_channel_name)

        object_settings = _new_object_settings(is_active=False)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-off', object_settings)

        # Five rejects out of ten messages are both too many rejects and too high an error rate - the HTTP
        # channel ruleset, loaded alongside, has nothing to say about either channel
        assert _rule_names(result) == ['Error_Rate', 'Negative_Acks']

        for _, _, body in recorder.emails:
            assert _other_channel_name in body
            assert _channel_name not in body

# ################################################################################################################################

    def test_a_streak_of_negative_acks_is_a_failing_channel(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_message(audit_log, engine, now, 'streak-0', 'AA')
        _seed_message(audit_log, engine, now, 'streak-1', 'AE')
        _seed_message(audit_log, engine, now, 'streak-2', 'AE')
        _seed_message(audit_log, engine, now, 'streak-3', 'AE')

        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-streak', None)

        assert 'Channel_Failing' in _rule_names(result)
        assert 'Negative_Acks' in _rule_names(result)

# ################################################################################################################################

    def test_the_traffic_expected_toggle_decides_whether_silence_is_measured(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # The one message the channel ever received is two hours old
        _seed_message(audit_log, engine, now, 'silent-1', 'AA', seconds_back=7200)

        # Off - the channel is never measured for silence ..
        object_settings = _new_object_settings(traffic_expected=False)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-silent-1', object_settings)

        assert result.raised_count == 0

        # .. on - an hour of silence is an alert, from the MLLP ruleset and from nowhere else.
        object_settings = _new_object_settings(traffic_expected=True)
        result, recorder = _run_sweep(engine, audit_log, now, 'cid-mllp-silent-2', object_settings)

        assert _rule_names(result) == ['Channel_Silent']

        _, _, body = recorder.emails[0]
        assert _channel_name in body

# ################################################################################################################################

    def test_the_silence_window_of_the_channel_is_what_it_is_measured_against(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Half an hour of silence - under the rule's hour, over the channel's own ten minutes
        _seed_message(audit_log, engine, now, 'window-1', 'AA', seconds_back=1800)

        object_settings = _new_object_settings(traffic_expected=True)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-silence-window-1', object_settings)

        assert result.raised_count == 0

        object_settings = _new_object_settings(traffic_expected=True, silence_window=600)
        result, _ = _run_sweep(engine, audit_log, now, 'cid-mllp-silence-window-2', object_settings)

        assert _rule_names(result) == ['Channel_Silent']

# ################################################################################################################################
# ################################################################################################################################
