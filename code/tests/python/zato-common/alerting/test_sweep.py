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
from zato.common.alerting.collectors import new_fact
from zato.common.alerting.config_map import Explain_With_LLM_Key
from zato.common.alerting.engine import AlertDefaults, AlertTransports
from zato.common.alerting.model import AlertAction
from zato.common.alerting.object_config import alert_type_file_transfer, encode_email_connection, Email_Conn_Type_IMAP, \
    get_defaults as get_object_defaults
from zato.common.alerting.sweep import build_fact_message, build_finding_link, read_outcome, run_sweep
from zato.common.api import Alerting, Incidents
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import get_source_label
from zato.common.monitoring.health import EndpointMetrics
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
_server_name = 'test-sweep-server'

# The channels the tests seed events and metrics for
_channel_name = 'hl7.sweep.channel'
_other_channel_name = 'hl7.sweep.other'

# The outgoing connection the link tests seed per-hop delivery failures for
_connection_name = 'CRM'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# ################################################################################################################################
# ################################################################################################################################

# The ruleset the sweep tests match through - one invoke-service rule with its config in the
# outcome keys and one email rule, both written the way the builder writes them.
_rules_text = """
rule
    test_restart_on_errors
docs
    A channel erroring on at least half its traffic has its restart service invoked.
when
    alert.source is 'mllp-channel' and
    alert.error_rate is at least 0.5
then
    outcome.action = 'invoke-service'
    outcome.service = 'test.channel.restart'

rule
    test_email_on_silence
docs
    A feed silent for ten minutes raises an email alert.
when
    alert.silent_seconds is at least 600
then
    outcome.action = 'email'
    outcome.severity = 'error'
""".strip()

# The rule an outgoing connection and its own health check are both judged by - one condition,
# one threshold, two streams counted apart.
_health_rules_text = """
rule
    test_connection_down
docs
    A connection failing three times in a row is considered down, and so is its health check.
when
    alert.source in ['rest-outgoing', 'rest-outgoing-health'] and
    alert.consecutive_failures is at least 3
then
    outcome.action = 'email'
    outcome.severity = 'error'
""".strip()

# ################################################################################################################################
# ################################################################################################################################

class _TransportRecorder:
    """ A stand-in for the real transports, remembering everything that went out.
    """
    def __init__(self) -> 'None':
        self.emails:'anylist' = []
        self.email_connections:'anylist' = []
        self.invocations:'anylist' = []
        self.publications:'anylist' = []
        self.posts:'anylist' = []

    def make(self) -> 'AlertTransports':
        out = AlertTransports()

        def send_email(addresses:'anylist', subject:'str', body:'str', email_connection:'str'='') -> 'None':
            self.emails.append((addresses, subject, body))
            self.email_connections.append(email_connection)

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

def _load_rules(text:'str', ruleset_name:'str'=Alerting.Ruleset_Name) -> 'rule_engine_rule_list':
    """ Builds runtime rules out of zrules text, the same way a stored version loads.
    """
    documents, errors = parse_data_details(text, ruleset_name)
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

def _seed_exchange(audit_log:'AuditLog', source:'str', cid:'str') -> 'None':
    """ Stores the failed request/response pair an outgoing connection leaves behind, the way
    its wrapper writes it - the request half goes out fine, the response half carries the failure.
    """
    _ = audit_log.insert(source, AuditEvent.Request_Sent, _connection_name, cid=cid, outcome=AuditOutcome.OK)
    _ = audit_log.insert(source, AuditEvent.Response_Received, _connection_name, cid=cid, outcome=AuditOutcome.Error)

# ################################################################################################################################
# ################################################################################################################################

class TestReadOutcome:

    def test_only_prefixed_targets_come_through_stripped(self) -> 'None':
        then = {
            'outcome.action': 'invoke-service',
            'outcome.service': 'test.channel.restart',
            'something.else': 'ignored',
        }

        outcome = read_outcome(then)

        assert outcome == {'action': 'invoke-service', 'service': 'test.channel.restart'}

# ################################################################################################################################
# ################################################################################################################################

class TestBuildFactMessage:

    def test_only_the_measures_that_were_taken_speak(self) -> 'None':
        fact = new_fact(AuditSource.MLLP_Channel, _channel_name)
        fact['error_rate'] = 0.75
        fact['error_count'] = 3
        fact['total_count'] = 4
        fact['window_seconds'] = 300

        message = build_fact_message('test_restart_on_errors', fact)

        assert 'error rate 75% (3 of 4 over 300s)' in message
        assert _channel_name in message
        assert 'outstanding' not in message
        assert 'silent' not in message

# ################################################################################################################################

    def test_a_failing_health_check_says_so_in_words(self) -> 'None':
        fact = new_fact(AuditSource.REST_Outgoing_Health, _connection_name)
        fact['consecutive_failures'] = 3

        message = build_fact_message('test_connection_down', fact)

        assert 'REST check failed 3 times' in message
        assert _connection_name in message

        # The measure already names the source, so it is not repeated in parentheses
        assert '(REST check)' not in message

# ################################################################################################################################

    def test_one_failed_check_is_not_pluralized(self) -> 'None':
        fact = new_fact(AuditSource.SOAP_Outgoing_Health, _connection_name)
        fact['consecutive_failures'] = 1

        message = build_fact_message('test_connection_down', fact)

        assert 'SOAP check failed 1 time' in message
        assert 'failed 1 times' not in message

# ################################################################################################################################

    def test_a_failing_connection_keeps_the_streak_phrase(self) -> 'None':
        fact = new_fact(AuditSource.REST_Outgoing, _connection_name)
        fact['consecutive_failures'] = 3

        message = build_fact_message('test_connection_down', fact)

        assert '3 consecutive failures' in message
        assert '(REST outgoing)' in message

# ################################################################################################################################

    def test_a_measure_that_reads_alike_names_its_source(self) -> 'None':
        """ An error rate is an error rate on either stream, so the source in parentheses
        is what says which of the two is being reported.
        """
        fact = new_fact(AuditSource.REST_Outgoing_Health, _connection_name)
        fact['error_rate'] = 0.75
        fact['error_count'] = 3
        fact['total_count'] = 4
        fact['window_seconds'] = 3600

        message = build_fact_message('test_error_rate', fact)

        assert '(REST check)' in message
        assert 'error rate 75% (3 of 4 over 3600s)' in message

# ################################################################################################################################

    def test_a_missing_arrival_says_how_long_and_against_what(self) -> 'None':
        fact = new_fact(AuditSource.File_Outgoing, 'Daily results')
        fact['seconds_since_last_arrival'] = 600
        fact['arrival_overdue_ratio'] = 2.0

        message = build_fact_message('test_arrival_overdue', fact)

        assert 'no file for 600s' in message
        assert '2.0x its arrival window since the last file' in message
        assert 'Daily results' in message

# ################################################################################################################################
# ################################################################################################################################

class TestSourceLabels:

    def test_every_source_has_a_name_a_person_can_read(self) -> 'None':
        """ An alert names the source of what it measured, so a source added without a label
        of its own takes the alert down with it.
        """
        for name in dir(AuditSource):

            if name.startswith('_'):
                continue

            source = getattr(AuditSource, name)
            label = get_source_label(source)

            assert label != source, name

# ################################################################################################################################
# ################################################################################################################################

class TestRunSweep:

    def test_a_matching_fact_dispatches_the_action_with_the_outcome_config(self) -> 'None':
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
        assert result.dispatched == [('test_restart_on_errors', AlertAction.Invoke_Service)]

        # The invoke-service outcome invokes the service it names with the remaining
        # outcome keys travelling as the action config
        assert len(recorder.invocations) == 1

        service, payload = recorder.invocations[0]
        assert service == 'test.channel.restart'
        assert payload['object_name'] == _channel_name
        assert payload['source'] == AuditSource.MLLP_Channel
        assert payload['action_config']['service'] == 'test.channel.restart'
        assert 'error rate 100% (2 of 2' in payload['message']

# ################################################################################################################################

    def test_a_ruleset_the_llm_explains_hands_its_alerts_to_the_explain_service(self) -> 'None':
        """ With the ruleset's explain_with_llm key on, the match goes to the explain service
        instead of the rule's own action - the payload carries the action and the deployment
        defaults so the service can run that action itself once the LLM has spoken.
        """
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        _seed_outcome(audit_log, 'sweep-explain-1', AuditOutcome.Error)

        rules = _load_rules(_rules_text)

        # The config screen writes the key onto every rule document of the type
        for rule in rules:
            rule.document[Explain_With_LLM_Key] = True

        defaults = AlertDefaults()
        defaults.email_to = _addresses
        defaults.email_from = 'alerts@example.com'

        result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-explain-1', now,
            defaults=defaults)

        # The rule's own action is what the sweep reports as dispatched ..
        assert result.dispatched == [('test_restart_on_errors', AlertAction.Invoke_Service)]

        # .. while the one invocation went to the explain service, not to the restart service ..
        assert len(recorder.invocations) == 1

        service, payload = recorder.invocations[0]
        assert service == Incidents.Service_Explain

        # .. with everything the service needs to deliver the alert itself.
        assert payload['action'] == AlertAction.Invoke_Service
        assert payload['action_config'] == {'service': 'test.channel.restart'}
        assert payload['defaults'] == {'email_to': _addresses, 'email_from': 'alerts@example.com', 'webhook_url': ''}
        assert payload['object_name'] == _channel_name
        assert payload['explanation'] == ''

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
            if rule.name == 'test_restart_on_errors':
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

        defaults = AlertDefaults()
        defaults.email_to = _addresses

        result = run_sweep(
            engine, rules, metrics_by_name, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-both-1', now,
            defaults=defaults)

        assert result.fact_count == 2
        assert result.raised_count == 2
        assert sorted(result.dispatched) == [
            ('test_email_on_silence', AlertAction.Email_Digest),
            ('test_restart_on_errors', AlertAction.Invoke_Service),
        ]

        # The email rule went out through the email transport with the default addresses
        assert len(recorder.emails) == 1
        assert recorder.emails[0][0] == _addresses

        # The invoke-service rule went out through the service transport
        assert len(recorder.invocations) == 1
        assert recorder.invocations[0][1]['object_name'] == _channel_name

# ################################################################################################################################

    def test_a_failing_check_and_failing_traffic_raise_one_alert_each(self) -> 'None':
        """ One connection failing on both streams is two alerts, not one counted twice -
        what is measured apart is reported apart.
        """
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        for index in range(3):
            _seed_exchange(audit_log, AuditSource.REST_Outgoing, f'sweep-call-{index}')
            _seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, f'sweep-check-{index}')

        rules = _load_rules(_health_rules_text)

        defaults = AlertDefaults()
        defaults.email_to = _addresses

        result = run_sweep(
            engine, rules, {}, AuditSource.REST_Outgoing, recorder.make(), audit_log, 'cid-health-1', now,
            defaults=defaults)

        # Two facts about the one connection, each raising its own alert
        assert result.fact_count == 2
        assert result.raised_count == 2
        assert result.deduplicated_count == 0
        assert len(recorder.emails) == 2

        bodies = []

        for _, _, body in recorder.emails:
            bodies.append(body)

        joined = '\n'.join(bodies)

        assert 'REST check failed 3 times' in joined
        assert '3 consecutive failures' in joined

# ################################################################################################################################

    def test_the_arrival_windows_reach_the_arrival_rule(self) -> 'None':
        """ The per-schedule windows travel from the caller through the sweep into the collector,
        the way the job intervals do, and a schedule past its own window raises an email alert.
        """
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        schedule_name = 'Daily results'

        # The newest arrival of the schedule, ten minutes back on a five-minute window
        event_id = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Delivered, 'sftp.backups',
            cid='sweep-arrival-1', outcome=AuditOutcome.OK, attrs={'schedule': schedule_name})

        statement = update(event_table)
        statement = statement.where(event_table.c.id == event_id)
        statement = statement.values(event_time_iso=(now - timedelta(seconds=600)).isoformat())

        with engine.begin() as connection:
            _ = connection.execute(statement)

        rules = _load_rules(_arrival_rules_text)

        defaults = AlertDefaults()
        defaults.email_to = _addresses

        result = run_sweep(
            engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-arrival-1', now,
            defaults=defaults, arrival_windows={schedule_name: 300})

        assert result.raised_count == 1
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]

        assert schedule_name in body
        assert 'no file for 600s' in body

# ################################################################################################################################

    def test_the_window_of_a_ruleset_reaches_the_collectors(self) -> 'None':
        """ A ruleset's window_seconds default is the window its type's sources are measured over -
        a failure two hours back counts within a day's window and not within ten minutes.
        """
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Message_Sent, 'sftp.window',
            cid='sweep-window-1', outcome=AuditOutcome.Error)

        statement = update(event_table)
        statement = statement.where(event_table.c.id == event_id)
        statement = statement.values(event_time_iso=(now - timedelta(seconds=7200)).isoformat())

        with engine.begin() as connection:
            _ = connection.execute(statement)

        defaults = AlertDefaults()
        defaults.email_to = _addresses

        # Over a day the failure is in the window ..
        recorder = _TransportRecorder()
        rules = _load_rules(_window_rules_text.format(window_seconds=86400), 'alerts_file_transfer')

        result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-window-1', now,
            defaults=defaults)

        assert result.raised_count == 1
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert 'over 86400s' in body

        # .. over ten minutes it is not.
        recorder = _TransportRecorder()
        rules = _load_rules(_window_rules_text.format(window_seconds=600), 'alerts_file_transfer')

        result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-window-2', now,
            defaults=defaults)

        assert result.raised_count == 0
        assert recorder.emails == []

# ################################################################################################################################
# ################################################################################################################################

# The connection the object settings tests seed failures for
_settings_object_name = 'sftp.settings'

# The other connection the same tests seed the same failures for, without settings of its own
_settings_other_name = 'sftp.other'

# The email connection the settings send the alerts through
_settings_imap_name = 'Ops mailbox'

# ################################################################################################################################

def _seed_transfer_failure(audit_log:'AuditLog', engine:'Engine', now:'datetime', object_name:'str', *, cid:'str',
    seconds_back:'int'=0) -> 'None':
    """ Stores one failed file transfer, moved back in time if asked to.
    """
    event_id = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Message_Sent, object_name, cid=cid,
        outcome=AuditOutcome.Error)

    if seconds_back:
        statement = update(event_table)
        statement = statement.where(event_table.c.id == event_id)
        statement = statement.values(event_time_iso=(now - timedelta(seconds=seconds_back)).isoformat())

        with engine.begin() as connection:
            _ = connection.execute(statement)

# ################################################################################################################################

def _new_object_settings(**values:'any_') -> 'anydict':
    """ The object settings of one file transfer connection at the defaults, with the given values on top.
    """
    settings = get_object_defaults(alert_type_file_transfer)
    settings.update(values)

    out = {alert_type_file_transfer: {_settings_object_name: settings}}
    return out

# ################################################################################################################################

def _run_settings_sweep(engine:'Engine', audit_log:'AuditLog', now:'datetime', rules_text:'str', cid:'str',
    object_settings:'anydict | None') -> 'tuple[SweepResult, _TransportRecorder]':
    """ Runs one sweep of the file transfer ruleset with the given object settings.
    """
    defaults = AlertDefaults()
    defaults.email_to = _addresses

    recorder = _TransportRecorder()
    rules = _load_rules(rules_text, 'alerts_file_transfer')

    result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, cid, now,
        defaults=defaults, object_settings=object_settings)

    return result, recorder

# ################################################################################################################################
# ################################################################################################################################

class TestObjectSettings:

    def test_an_inactive_object_raises_nothing_while_the_others_still_do(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_transfer_failure(audit_log, engine, now, _settings_object_name, cid='settings-inactive-1')
        _seed_transfer_failure(audit_log, engine, now, _settings_other_name, cid='settings-inactive-2')

        object_settings = _new_object_settings(is_active=False)
        rules_text = _window_rules_text.format(window_seconds=86400)

        result, recorder = _run_settings_sweep(engine, audit_log, now, rules_text, 'cid-settings-inactive', object_settings)

        assert result.raised_count == 1
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _settings_other_name in body
        assert _settings_object_name not in body

# ################################################################################################################################

    def test_a_toggle_that_is_off_mutes_its_rule_for_that_object(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_transfer_failure(audit_log, engine, now, _settings_object_name, cid='settings-toggle-1')

        # Off - the rule the toggle stands for never sees the object ..
        object_settings = _new_object_settings(test_transfers=False)
        result, recorder = _run_settings_sweep(engine, audit_log, now, _toggle_rules_text, 'cid-settings-toggle-1',
            object_settings)

        assert result.raised_count == 0
        assert recorder.emails == []

        # .. on - it does.
        object_settings = _new_object_settings(test_transfers=True)
        result, recorder = _run_settings_sweep(engine, audit_log, now, _toggle_rules_text, 'cid-settings-toggle-2',
            object_settings)

        assert result.raised_count == 1
        assert len(recorder.emails) == 1

# ################################################################################################################################

    def test_the_objects_own_number_stands_in_for_the_rules_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_transfer_failure(audit_log, engine, now, _settings_object_name, cid='settings-threshold-1')

        # The rule asks for five failures and there is one - nothing without settings ..
        rules_text = _threshold_rules_text.format(warning_failure_count=5)
        result, recorder = _run_settings_sweep(engine, audit_log, now, rules_text, 'cid-settings-threshold-1', None)

        assert result.raised_count == 0

        # .. and an alert once the object itself asks for one.
        object_settings = _new_object_settings(warning_failures=1)
        result, recorder = _run_settings_sweep(engine, audit_log, now, rules_text, 'cid-settings-threshold-2',
            object_settings)

        assert result.raised_count == 1
        assert len(recorder.emails) == 1

# ################################################################################################################################

    def test_the_objects_own_window_is_what_it_is_measured_over(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A failure two hours back for both connections
        _seed_transfer_failure(audit_log, engine, now, _settings_object_name, cid='settings-window-1', seconds_back=7200)
        _seed_transfer_failure(audit_log, engine, now, _settings_other_name, cid='settings-window-2', seconds_back=7200)

        # The ruleset measures over a day, the object over ten minutes - only the other connection is in the window
        object_settings = _new_object_settings(warning_failures=1, window=600)
        rules_text = _window_rules_text.format(window_seconds=86400)

        result, recorder = _run_settings_sweep(engine, audit_log, now, rules_text, 'cid-settings-window-1', object_settings)

        assert result.raised_count == 1

        _, _, body = recorder.emails[0]
        assert _settings_other_name in body
        assert 'over 86400s' in body

        # The other way round - the ruleset measures over ten minutes, the object over a day
        object_settings = _new_object_settings(warning_failures=1, window=86400)
        rules_text = _window_rules_text.format(window_seconds=600)

        result, recorder = _run_settings_sweep(engine, audit_log, now, rules_text, 'cid-settings-window-2', object_settings)

        assert result.raised_count == 1

        _, _, body = recorder.emails[0]
        assert _settings_object_name in body
        assert 'over 86400s' in body

# ################################################################################################################################

    def test_the_objects_own_email_connection_reaches_the_transport(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_transfer_failure(audit_log, engine, now, _settings_object_name, cid='settings-email-1')
        _seed_transfer_failure(audit_log, engine, now, _settings_other_name, cid='settings-email-2')

        email_connection = encode_email_connection(Email_Conn_Type_IMAP, _settings_imap_name)
        object_settings = _new_object_settings(warning_failures=1, email_connection=email_connection)
        rules_text = _window_rules_text.format(window_seconds=86400)

        result, recorder = _run_settings_sweep(engine, audit_log, now, rules_text, 'cid-settings-email', object_settings)

        assert result.raised_count == 2

        # The object's alert names its connection, the other one leaves through the default
        by_object = {}
        for (_, _, body), connection in zip(recorder.emails, recorder.email_connections):
            if _settings_object_name in body:
                by_object[_settings_object_name] = connection
            else:
                by_object[_settings_other_name] = connection

        assert by_object == {_settings_object_name: email_connection, _settings_other_name: ''}

# ################################################################################################################################
# ################################################################################################################################

# The rule the toggle test matches through - the seeded Test_Transfer_Failing rule's name over
# a plain failure count, so the test transfers toggle is what decides whether it fires.
_toggle_rules_text = """
rule
    Test_Transfer_Failing
docs
    A connection with any failed transfer raises an email alert.
defaults
    window_seconds = 86400
when
    alert.source is 'file-outgoing' and
    alert.error_count is at least 1
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# The rule the threshold test matches through - the seeded Transfer_Failures rule's shape with
# the warning count left to the test, so an object's own number can stand in for it.
_threshold_rules_text = """
rule
    Transfer_Failures
docs
    A file transfer connection with enough failed transfers within the window raises an email alert.
defaults
    warning_failure_count = {warning_failure_count}
    window_seconds = 86400
when
    alert.source is 'file-outgoing' and
    alert.error_count is at least default.warning_failure_count
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################
# ################################################################################################################################

# The ruleset the window test matches through - the seeded Transfer_Failures rule's shape under
# the file transfer ruleset's name, so the config map reads its window the way the sweep does.
_window_rules_text = """
rule
    Transfer_Failures
docs
    A file transfer connection with any failed transfer within the window raises an email alert.
defaults
    warning_failure_count = 1
    window_seconds = {window_seconds}
when
    alert.source is 'file-outgoing' and
    alert.error_count is at least default.warning_failure_count
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################
# ################################################################################################################################

# The ruleset the arrival test matches through - a schedule past its own arrival window
# raises an email alert, with the same condition the seeded Arrival_Overdue rule has.
_arrival_rules_text = """
rule
    test_arrival_overdue
docs
    A schedule whose expected file did not arrive within its own window raises an email alert.
when
    alert.source is 'file-outgoing' and
    alert.arrival_overdue_ratio is at least 1
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################
# ################################################################################################################################

# The ruleset the link tests match through - one rule watching the per-hop delivery
# failures of outgoing connections and one carrying a link of its own.
_link_rules_text = """
rule
    test_link_on_delivery_errors
docs
    An outgoing connection erroring on at least half its traffic raises an alert.
when
    alert.source is 'rest-outgoing' and
    alert.error_rate is at least 0.5
then
    outcome.action = 'invoke-service'
    outcome.service = 'demo.remediate'
""".strip()

_own_link_rules_text = """
rule
    test_own_link_on_delivery_errors
docs
    An outgoing connection erroring on at least half its traffic raises an alert
    pointing at its own runbook.
when
    alert.source is 'rest-outgoing' and
    alert.error_rate is at least 0.5
then
    outcome.action = 'invoke-service'
    outcome.service = 'demo.remediate'
    outcome.link = 'https://example.com/runbook'
""".strip()

# ################################################################################################################################

def _seed_hop_failure(audit_log:'AuditLog', cid:'str') -> 'int':
    """ Stores one failed per-hop delivery - the request-sent event type its source
    declared resubmittable.
    """
    out = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _connection_name,
        cid=cid, outcome=AuditOutcome.Error)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFindingLinks:

    def test_a_resubmittable_failure_deep_links_at_the_failing_event(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        _ = _seed_hop_failure(audit_log, 'link-deep-1')
        newest_id = _seed_hop_failure(audit_log, 'link-deep-2')

        rules = _load_rules(_link_rules_text)

        result = run_sweep(engine, rules, {}, AuditSource.REST_Outgoing, recorder.make(), audit_log, 'cid-link-1', now)

        assert result.raised_count == 1
        assert len(recorder.invocations) == 1

        # The link is the audit log page pointed straight at the newest failing event,
        # with the resubmit confirmation asked to open on it
        link = recorder.invocations[0][1]['link']
        assert link == (
            f'/zato/audit-log/?source=rest-outgoing&object_name={_connection_name}&cluster=1'
            f'&event={newest_id}&action=resubmit')

# ################################################################################################################################

    def test_a_failure_no_source_declared_resubmittable_keeps_the_plain_link(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        # An outbound acknowledgment failing is no resubmittable event type
        _seed_outcome(audit_log, 'link-plain-1', AuditOutcome.Error)

        rules = _load_rules(_rules_text)

        result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, 'cid-link-2', now)

        assert result.raised_count == 1
        assert len(recorder.invocations) == 1

        # The link is the same page filtered down to the object, with no event to open
        link = recorder.invocations[0][1]['link']
        assert link == f'/zato/audit-log/?source=mllp-channel&object_name={_channel_name}&cluster=1'

# ################################################################################################################################

    def test_a_rule_with_a_link_of_its_own_keeps_it(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        _ = _seed_hop_failure(audit_log, 'link-own-1')

        rules = _load_rules(_own_link_rules_text)

        result = run_sweep(engine, rules, {}, AuditSource.REST_Outgoing, recorder.make(), audit_log, 'cid-link-3', now)

        assert result.raised_count == 1
        assert len(recorder.invocations) == 1
        assert recorder.invocations[0][1]['link'] == 'https://example.com/runbook'

# ################################################################################################################################

    def test_the_dashboard_address_leads_the_link_when_configured(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        newest_id = _seed_hop_failure(audit_log, 'link-dash-1')

        rules = _load_rules(_link_rules_text)

        result = run_sweep(engine, rules, {}, AuditSource.REST_Outgoing, recorder.make(), audit_log, 'cid-link-4', now,
            dashboard_url='https://dashboard.example.com/')

        assert result.raised_count == 1
        assert len(recorder.invocations) == 1

        # The notification carries a full address - the dashboard first, the page's path after it
        link = recorder.invocations[0][1]['link']
        assert link == (
            f'https://dashboard.example.com/zato/audit-log/?source=rest-outgoing'
            f'&object_name={_connection_name}&cluster=1&event={newest_id}&action=resubmit')

# ################################################################################################################################

    def test_the_link_builder_reads_the_facts_own_measures(self) -> 'None':
        fact = new_fact(AuditSource.REST_Outgoing, _connection_name)
        fact['last_error_event_id'] = 123
        fact['is_resubmittable'] = 1

        link = build_finding_link(fact)

        assert link == f'/zato/audit-log/?source=rest-outgoing&object_name={_connection_name}&cluster=1&event=123&action=resubmit'

# ################################################################################################################################
# ################################################################################################################################
