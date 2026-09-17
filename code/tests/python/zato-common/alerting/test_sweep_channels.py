# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.engine import AlertDefaults, AlertTransports
from zato.common.alerting.object_config import alert_type_channels, encode_email_connection, Email_Conn_Type_IMAP, \
    get_defaults as get_object_defaults, LLM_Connection_Config_Key
from zato.common.alerting.seed.rules_common import channels_rules
from zato.common.alerting.sweep import run_sweep
from zato.common.api import Alerting
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
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
_server_name = 'test-sweep-channels-server'

# The ruleset the channels are judged by - the one the seed ships
_ruleset_name = 'alerts_channels'

# The REST channel with settings of its own and the one without any
_channel_name = 'orders.api'
_other_channel_name = 'orders.status'

# The caller the rejected calls authenticate as
_caller = 'partner-a'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# The connections the settings route the alerts through
_imap_name = 'Ops mailbox'
_llm_name = 'ops.llm'

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

def _load_channel_rules() -> 'rule_engine_rule_list':
    """ The seeded channel rules as runtime rules, all of them active.
    """
    documents, errors = parse_data_details(channels_rules, _ruleset_name)
    assert errors == []

    loaded = load_documents(documents)

    out = []
    for full_name in loaded.rule_names:
        out.append(loaded.manager[full_name])

    return out

# ################################################################################################################################

def _seed_call(audit_log:'AuditLog', engine:'Engine', now:'datetime', cid:'str', status:'str', *,
    object_name:'str'=_channel_name, seconds_back:'int'=0, source:'str'=AuditSource.REST_Channel) -> 'None':
    """ Stores the request and response pair one call of a channel leaves behind, moved back in time if asked to.
    """
    if status.startswith('2'):
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    request_id = audit_log.insert(source, AuditEvent.Request_Received, object_name, cid=cid,
        outcome=AuditOutcome.OK, ext_client_id=_caller)

    response_id = audit_log.insert(source, AuditEvent.Response_Sent, object_name, cid=cid,
        outcome=outcome, status=status, ext_client_id=_caller, duration_ms=20)

    if seconds_back:
        event_time_iso = (now - timedelta(seconds=seconds_back)).isoformat()

        statement = update(event_table)
        statement = statement.where(event_table.c.id.in_([request_id, response_id]))
        statement = statement.values(event_time_iso=event_time_iso)

        with engine.begin() as connection:
            _ = connection.execute(statement)

# ################################################################################################################################

def _seed_rejections(audit_log:'AuditLog', engine:'Engine', now:'datetime', prefix:'str', count:'int', *,
    object_name:'str'=_channel_name, seconds_back:'int'=0, source:'str'=AuditSource.REST_Channel) -> 'None':
    """ Stores the given number of calls a channel answered with a 401, each followed by a call that went through,
    so the rejections never form an unbroken streak and only the rules about counts and rates see them.
    """
    for idx in range(count):
        _seed_call(audit_log, engine, now, f'{prefix}-{idx}-rejected', '401 Unauthorized', object_name=object_name,
            seconds_back=seconds_back, source=source)
        _seed_call(audit_log, engine, now, f'{prefix}-{idx}-ok', '200 OK', object_name=object_name,
            seconds_back=seconds_back, source=source)

# ################################################################################################################################

def _new_object_settings(**values:'any_') -> 'anydict':
    """ The object settings of one REST channel at the defaults, with the given values on top.
    The LLM stays out of it unless a test asks for it, so the actions run directly and can be observed.
    """
    settings = get_object_defaults(alert_type_channels)
    settings['use_llm'] = False
    settings.update(values)

    out = {alert_type_channels: {_channel_name: settings}}
    return out

# ################################################################################################################################

def _run_channel_sweep(engine:'Engine', audit_log:'AuditLog', now:'datetime', cid:'str',
    object_settings:'anydict | None') -> 'tuple[SweepResult, _TransportRecorder]':
    """ Runs one sweep of the seeded channel ruleset with the given object settings.
    """
    defaults = AlertDefaults()
    defaults.email_to = _addresses

    recorder = _TransportRecorder()
    rules = _load_channel_rules()

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

class TestChannelSweep:

    def test_a_channel_with_alerts_off_is_skipped_while_another_still_raises(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_rejections(audit_log, engine, now, 'off-a', 10)
        _seed_rejections(audit_log, engine, now, 'off-b', 10, object_name=_other_channel_name)

        object_settings = _new_object_settings(is_active=False)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-channels-off', object_settings)

        # Ten rejections out of twenty calls are both too many rejections and too high an error rate
        assert _rule_names(result) == ['Auth_Failures', 'Channel_Error_Rate']
        assert len(recorder.emails) == 2

        for _, _, body in recorder.emails:
            assert _other_channel_name in body
            assert _channel_name not in body

        # Without settings of its own, the other channel is emailed through the default connection
        assert recorder.email_connections == ['', '']

# ################################################################################################################################

    def test_the_channels_own_threshold_stands_in_for_the_rules_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_rejections(audit_log, engine, now, 'own', 3)

        # The rule asks for ten rejections and there are three - nothing without settings ..
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-channels-threshold-1', None)

        assert result.raised_count == 0
        assert recorder.emails == []

        # .. and an alert once the channel itself asks for three.
        object_settings = _new_object_settings(auth_failures=3)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-channels-threshold-2', object_settings)

        assert _rule_names(result) == ['Auth_Failures']
        assert len(recorder.emails) == 1

# ################################################################################################################################

    def test_the_traffic_expected_toggle_decides_whether_silence_is_measured(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # The one call the channel ever received is two hours old
        _seed_call(audit_log, engine, now, 'silent-1', '200', seconds_back=7200)

        # Off - the channel is never measured for silence ..
        object_settings = _new_object_settings(traffic_expected=False)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-channels-silent-1', object_settings)

        assert result.raised_count == 0

        # .. on - an hour of silence is an alert.
        object_settings = _new_object_settings(traffic_expected=True)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-channels-silent-2', object_settings)

        assert _rule_names(result) == ['Channel_Silent']

        _, _, body = recorder.emails[0]
        assert _channel_name in body

# ################################################################################################################################

    def test_the_silence_window_of_the_channel_is_what_it_is_measured_against(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Half an hour of silence - under the rule's hour, over the channel's own ten minutes
        _seed_call(audit_log, engine, now, 'window-1', '200', seconds_back=1800)

        object_settings = _new_object_settings(traffic_expected=True)
        result, _ = _run_channel_sweep(engine, audit_log, now, 'cid-channels-silence-window-1', object_settings)

        assert result.raised_count == 0

        object_settings = _new_object_settings(traffic_expected=True, silence_window=600)
        result, _ = _run_channel_sweep(engine, audit_log, now, 'cid-channels-silence-window-2', object_settings)

        assert _rule_names(result) == ['Channel_Silent']

# ################################################################################################################################

    def test_the_rejected_callers_have_a_window_of_their_own(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Ten rejections an hour and a half back for both channels
        _seed_rejections(audit_log, engine, now, 'win-a', 10, seconds_back=5400)
        _seed_rejections(audit_log, engine, now, 'win-b', 10, object_name=_other_channel_name, seconds_back=5400)

        # The rule measures over five minutes, the channel over two hours - only the channel is alerted on,
        # and its error rate, measured over its own five minutes, sees nothing.
        object_settings = _new_object_settings(auth_failures_window=7200)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-channels-auth-window', object_settings)

        assert _rule_names(result) == ['Auth_Failures']

        _, _, body = recorder.emails[0]
        assert _channel_name in body
        assert _other_channel_name not in body

# ################################################################################################################################

    def test_the_channels_own_llm_connection_rides_in_the_outcome(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_rejections(audit_log, engine, now, 'conn-a', 3)
        _seed_rejections(audit_log, engine, now, 'conn-b', 3, object_name=_other_channel_name)

        # The channel with settings is explained through its own LLM connection, with its own threshold in the payload ..
        object_settings = _new_object_settings(auth_failures=3, use_llm=True, llm_connection=_llm_name)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-channels-connections', object_settings)

        assert _rule_names(result) == ['Auth_Failures']
        assert len(recorder.invocations) == 1

        service, payload = recorder.invocations[0]
        assert service == Alerting.Service_Explain
        assert payload['object_name'] == _channel_name
        assert payload['action_config'][LLM_Connection_Config_Key] == _llm_name
        assert payload['fact']['auth_failure_count'] == 3
        assert payload['thresholds'] == {'auth_failure_threshold': 3, 'window_seconds': 300}

        # .. and the other channel, at the default of ten, is not alerted on at all.
        assert recorder.emails == []

# ################################################################################################################################

    def test_the_channels_own_email_connection_reaches_the_transport(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_rejections(audit_log, engine, now, 'email-a', 3)

        email_connection = encode_email_connection(Email_Conn_Type_IMAP, _imap_name)
        object_settings = _new_object_settings(auth_failures=3, email_connection=email_connection)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-channels-email', object_settings)

        assert _rule_names(result) == ['Auth_Failures']
        assert recorder.email_connections == [email_connection]

# ################################################################################################################################
# ################################################################################################################################

class TestSoapChannelSweep:

    def test_the_soap_channels_own_threshold_fires_on_its_own_facts(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_rejections(audit_log, engine, now, 'soap-own', 3, source=AuditSource.SOAP_Channel)

        # Three rejections are under the rule's ten - nothing without settings ..
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-soap-threshold-1', None)

        assert result.raised_count == 0

        # .. and an alert on the SOAP channel's facts once the channel itself asks for three.
        object_settings = _new_object_settings(auth_failures=3, use_llm=True, llm_connection=_llm_name)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-soap-threshold-2', object_settings)

        assert _rule_names(result) == ['Auth_Failures']

        _, payload = recorder.invocations[0]
        assert payload['source'] == AuditSource.SOAP_Channel
        assert payload['object_name'] == _channel_name
        assert payload['fact']['auth_failure_count'] == 3

# ################################################################################################################################

    def test_a_soap_channel_with_alerts_off_is_skipped(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_rejections(audit_log, engine, now, 'soap-off', 10, source=AuditSource.SOAP_Channel)

        object_settings = _new_object_settings(is_active=False)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-soap-off', object_settings)

        assert result.raised_count == 0
        assert recorder.emails == []

# ################################################################################################################################

    def test_a_soap_channels_silence_and_its_own_window_are_measured(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # The one call the SOAP channel ever received is half an hour old - under the rule's hour,
        # over the channel's own ten minutes
        _seed_call(audit_log, engine, now, 'soap-silent-1', '200', seconds_back=1800, source=AuditSource.SOAP_Channel)

        object_settings = _new_object_settings(traffic_expected=True)
        result, _ = _run_channel_sweep(engine, audit_log, now, 'cid-soap-silence-1', object_settings)

        assert result.raised_count == 0

        object_settings = _new_object_settings(traffic_expected=True, silence_window=600)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-soap-silence-2', object_settings)

        assert _rule_names(result) == ['Channel_Silent']

        _, _, body = recorder.emails[0]
        assert _channel_name in body

# ################################################################################################################################

    def test_a_rest_and_a_soap_channel_of_one_name_are_alerted_on_apart(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Only the SOAP channel of the name has enough rejections
        _seed_rejections(audit_log, engine, now, 'pair-rest', 1)
        _seed_rejections(audit_log, engine, now, 'pair-soap', 3, source=AuditSource.SOAP_Channel)

        object_settings = _new_object_settings(auth_failures=3, use_llm=True, llm_connection=_llm_name)
        result, recorder = _run_channel_sweep(engine, audit_log, now, 'cid-soap-pair', object_settings)

        assert _rule_names(result) == ['Auth_Failures']
        assert len(recorder.invocations) == 1

        _, payload = recorder.invocations[0]
        assert payload['source'] == AuditSource.SOAP_Channel

# ################################################################################################################################
# ################################################################################################################################
