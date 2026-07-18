# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.alerting.engine import build_digest, build_slack_payload, build_teams_payload, process_findings, \
    AlertTransports
from zato.common.alerting.model import new_finding, new_rule, AlertAction, AlertSeverity, FindingKind
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditSource
from zato.common.json_internal import loads
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-alerting-server'

# The channel the tests raise findings about
_channel_name = 'hl7.test.channel'

# The webhook the Slack and Teams rules post to
_webhook_url = 'https://hooks.example.com/services/T000/B000/XXX'

# The addresses the email rules send to
_addresses = ['ops@example.com']

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

        out.send_email = lambda addresses, subject, body: self.emails.append((addresses, subject, body))
        out.invoke_service = lambda service, payload: self.invocations.append((service, payload))
        out.publish = lambda topic, payload: self.publications.append((topic, payload))
        out.http_post = lambda url, payload: self.posts.append((url, payload))

        return out

# ################################################################################################################################

def _new_finding(*, severity:'str'=AlertSeverity.Warning) -> 'stranydict':
    out = new_finding(FindingKind.Feed_Silent, AuditSource.HL7, _channel_name,
        'Feed on `hl7.test.channel` silent for 400s', link='/zato/hl7/channels/', severity=severity)
    return out

# ################################################################################################################################

def _count_alert_events() -> 'int':
    engine = get_audit_engine()

    query = select(event_table).where(event_table.c.event_type == AuditEvent.Alert_Raised)

    with engine.connect() as connection:
        out = len(connection.execute(query).fetchall())

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestActions:

    def test_the_email_action_sends_to_the_rule_addresses(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('silent-feeds', FindingKind.Feed_Silent,
            action=AlertAction.Email_Digest, action_config={'addresses': _addresses})

        result = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-email', utcnow())

        assert result.raised_count == 1
        assert result.dispatched == [('silent-feeds', AlertAction.Email_Digest)]

        addresses, subject, body = recorder.emails[0]

        assert addresses == _addresses
        assert 'silent for 400s' in subject
        assert '/zato/hl7/channels/' in body

# ################################################################################################################################

    def test_the_invoke_service_action_carries_the_structured_payload(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('remediate', FindingKind.Feed_Silent,
            action=AlertAction.Invoke_Service, action_config={'service': 'hl7.channel.restart'})

        _ = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-invoke', utcnow())

        service, payload = recorder.invocations[0]

        assert service == 'hl7.channel.restart'
        assert payload['rule'] == 'remediate'
        assert payload['kind'] == FindingKind.Feed_Silent
        assert payload['object_name'] == _channel_name
        assert payload['severity'] == AlertSeverity.Warning
        assert payload['count'] == 1
        assert isinstance(payload['alert_id'], int)

# ################################################################################################################################

    def test_the_publish_action_carries_the_same_payload_to_a_topic(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('advisories', FindingKind.Feed_Silent,
            action=AlertAction.Publish_To_Topic, action_config={'topic': 'zato.alerts'})

        _ = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-publish', utcnow())

        topic, payload = recorder.publications[0]

        assert topic == 'zato.alerts'
        assert payload['message'] == 'Feed on `hl7.test.channel` silent for 400s'

# ################################################################################################################################

    def test_the_slack_action_posts_to_the_webhook(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('slack-ops', FindingKind.Feed_Silent,
            action=AlertAction.Slack, action_config={'webhook_url': _webhook_url})

        _ = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-slack', utcnow())

        url, payload = recorder.posts[0]

        assert url == _webhook_url
        assert payload == {'text': 'Feed on `hl7.test.channel` silent for 400s\n/zato/hl7/channels/'}

# ################################################################################################################################

    def test_the_teams_action_posts_a_message_card(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('teams-ops', FindingKind.Feed_Silent,
            action=AlertAction.Teams, action_config={'webhook_url': _webhook_url})

        _ = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-teams', utcnow())

        url, payload = recorder.posts[0]

        assert url == _webhook_url
        assert payload['@type'] == 'MessageCard'
        assert payload['summary'] == 'Feed on `hl7.test.channel` silent for 400s'
        assert payload['themeColor'] == 'e8a317'
        assert 'silent for 400s' in payload['text']
        assert '/zato/hl7/channels/' in payload['text']

# ################################################################################################################################

    def test_a_critical_teams_card_is_red(self) -> 'None':
        payload = build_teams_payload('The channel is down', '', AlertSeverity.Critical)

        assert payload['themeColor'] == 'cc0000'
        assert payload['text'] == 'The channel is down'

# ################################################################################################################################

    def test_a_slack_payload_without_a_link_is_just_the_message(self) -> 'None':
        payload = build_slack_payload('The channel is down', '')

        assert payload == {'text': 'The channel is down'}

# ################################################################################################################################
# ################################################################################################################################

class TestDedupAndCriticalFloor:

    def test_a_repetition_is_not_dispatched_but_is_still_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()
        transports = recorder.make()
        now = utcnow()

        rule = new_rule('slack-ops', FindingKind.Feed_Silent,
            action=AlertAction.Slack, action_config={'webhook_url': _webhook_url})

        first = process_findings([rule], [_new_finding()], transports, audit_log, 'cid-quiet-1', now)
        second = process_findings([rule], [_new_finding()], transports, audit_log, 'cid-quiet-2', now)

        # The repetition was deduplicated and not dispatched again ..
        assert first.raised_count == 1
        assert second.raised_count == 0
        assert second.deduplicated_count == 1
        assert len(recorder.posts) == 1

        # .. yet both occurrences are in the audit trail, the second with its count.
        assert _count_alert_events() == 2

# ################################################################################################################################

    def test_a_critical_finding_is_never_suppressed(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()
        transports = recorder.make()
        now = utcnow()

        rule = new_rule('slack-ops', FindingKind.Feed_Silent,
            action=AlertAction.Slack, action_config={'webhook_url': _webhook_url})

        critical = _new_finding(severity=AlertSeverity.Critical)

        _ = process_findings([rule], [critical], transports, audit_log, 'cid-critical-1', now)
        second = process_findings([rule], [critical], transports, audit_log, 'cid-critical-2', now)

        # Deduplicated in the store - dispatched anyway, with the count prefix
        assert second.deduplicated_count == 1
        assert len(recorder.posts) == 2

        _, payload = recorder.posts[1]
        assert payload['text'].startswith('[2x] ')

# ################################################################################################################################
# ################################################################################################################################

class TestDefaultSink:

    def test_an_unmatched_finding_never_vanishes(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        # The one rule cares about a different kind
        rule = new_rule('error-rates', FindingKind.Error_Rate,
            action=AlertAction.Slack, action_config={'webhook_url': _webhook_url})

        result = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-sink', utcnow())

        assert result.raised_count == 0
        assert len(result.unmatched) == 1
        assert recorder.posts == []

# ################################################################################################################################

    def test_the_catch_all_digest_goes_to_the_default_address(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        result = process_findings([], [_new_finding()], recorder.make(), audit_log, 'cid-catch-all', utcnow(),
            default_email=_addresses, dashboard_url='https://dashboard.example.com')

        assert len(result.unmatched) == 1

        addresses, subject, body = recorder.emails[0]

        assert addresses == _addresses
        assert subject == 'Zato alert digest - 1 finding'
        assert 'silent for 400s' in body
        assert 'https://dashboard.example.com/zato/hl7/channels/' in body

# ################################################################################################################################
# ################################################################################################################################

class TestAuditTrail:

    def test_every_occurrence_is_an_alert_raised_event(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('slack-ops', FindingKind.Feed_Silent,
            action=AlertAction.Slack, action_config={'webhook_url': _webhook_url})

        _ = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-trail', utcnow())

        engine = get_audit_engine()

        query = select(event_table).where(event_table.c.event_type == AuditEvent.Alert_Raised)

        with engine.connect() as connection:
            rows = connection.execute(query).fetchall()

        assert len(rows) == 1

        row = dict(rows[0]._mapping)

        assert row['source'] == AuditSource.HL7
        assert row['object_name'] == _channel_name
        assert row['cid'] == 'cid-trail'

        details = loads(row['data'])

        assert details['rule'] == 'slack-ops'
        assert details['kind'] == FindingKind.Feed_Silent
        assert details['count'] == 1

# ################################################################################################################################

    def test_multiple_matching_rules_each_fire(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        # A finding may match multiple rules, each dispatching independently
        slack_rule = new_rule('slack-ops', FindingKind.Feed_Silent,
            action=AlertAction.Slack, action_config={'webhook_url': _webhook_url})
        teams_rule = new_rule('teams-ops', FindingKind.Feed_Silent,
            action=AlertAction.Teams, action_config={'webhook_url': _webhook_url})

        result = process_findings([slack_rule, teams_rule], [_new_finding()], recorder.make(),
            audit_log, 'cid-both', utcnow())

        assert result.raised_count == 2
        assert len(recorder.posts) == 2
        assert _count_alert_events() == 2

# ################################################################################################################################

    def test_the_digest_builder_counts_its_findings(self) -> 'None':
        first = _new_finding()
        second = _new_finding()

        subject, body = build_digest([first, second])

        assert subject == 'Zato alert digest - 2 findings'
        assert body.count('silent for 400s') == 2

# ################################################################################################################################
# ################################################################################################################################
