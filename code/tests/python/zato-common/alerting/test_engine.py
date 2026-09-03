# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.alerting.engine import build_digest, process_findings, AlertDefaults, AlertTransports
from zato.common.alerting.model import new_finding, new_rule, AlertAction, AlertSeverity, FindingKind
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditSource
from zato.common.json_internal import loads
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.alerting.model import Finding
    from zato.common.typing_ import any_, anylist, stranydict
    any_ = any_
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-alerting-server'

# The channel the tests raise findings about
_channel_name = 'hl7.test.channel'

# The URL the plain webhook rules post to
_webhook_url = 'https://example.atlassian.net/automation/webhooks/abc'

# The channel the Slack rules post to
_slack_channel = '#zato-alerts'

# The team and channel the Teams rules post to
_teams_to = 'Zato Ops/Alerts'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# ################################################################################################################################

def _email_defaults() -> 'AlertDefaults':
    """ The deployment-level defaults with only the email address configured.
    """
    out = AlertDefaults()
    out.email_to = _addresses
    return out

# ################################################################################################################################
# ################################################################################################################################

class _TransportRecorder:
    """ A stand-in for the real transports, remembering everything that went out.
    """
    def __init__(self) -> 'None':
        self.emails:'anylist' = []
        self.invocations:'anylist' = []
        self.publications:'anylist' = []
        self.slack_messages:'anylist' = []
        self.teams_messages:'anylist' = []
        self.posts:'anylist' = []

        # When set, the Slack transport raises this many times before it starts recording.
        self.slack_failures_left = 0

# ################################################################################################################################

    def make(self) -> 'AlertTransports':
        out = AlertTransports()

        def send_email(addresses:'anylist', subject:'str', body:'str') -> 'None':
            self.emails.append((addresses, subject, body))

        def invoke_service(service:'str', payload:'stranydict') -> 'None':
            self.invocations.append((service, payload))

        def publish(topic:'str', payload:'stranydict') -> 'None':
            self.publications.append((topic, payload))

        def send_slack(channel:'str', text:'str') -> 'None':

            if self.slack_failures_left:
                self.slack_failures_left -= 1
                raise Exception('The Slack connection is not reachable')

            self.slack_messages.append((channel, text))

        def send_teams(to:'str', html:'str') -> 'None':
            self.teams_messages.append((to, html))

        def http_post(url:'str', payload:'stranydict') -> 'None':
            self.posts.append((url, payload))

        out.send_email = send_email
        out.invoke_service = invoke_service
        out.publish = publish
        out.send_slack = send_slack
        out.send_teams = send_teams
        out.http_post = http_post

        return out

# ################################################################################################################################

def _new_finding(*, severity:'str'=AlertSeverity.Warning) -> 'Finding':
    out = new_finding(FindingKind.Feed_Silent, AuditSource.MLLP_Channel, _channel_name,
        'Feed on `hl7.test.channel` silent for 400s', link='/zato/hl7/channels/', severity=severity)
    return out

# ################################################################################################################################

def _count_alert_events() -> 'int':
    engine = get_audit_engine()

    query = select(event_table).where(event_table.c.event_type == AuditEvent.Alert_Raised)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    out = len(rows)
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

    def test_an_email_rule_without_addresses_uses_the_default_address(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('silent-feeds-default', FindingKind.Feed_Silent, action=AlertAction.Email_Digest)

        result = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-email-default', utcnow(),
            defaults=_email_defaults())

        assert result.dispatched == [('silent-feeds-default', AlertAction.Email_Digest)]

        addresses, subject, _ = recorder.emails[0]

        assert addresses == _addresses
        assert 'silent for 400s' in subject

# ################################################################################################################################

    def test_an_email_rule_without_any_addresses_sends_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('silent-feeds-nowhere', FindingKind.Feed_Silent, action=AlertAction.Email_Digest)

        result = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-email-nowhere', utcnow())

        # The alert itself is still raised, only the email delivery is skipped
        assert result.raised_count == 1
        assert recorder.emails == []

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

    def test_the_slack_action_sends_to_the_rule_channel(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('slack-ops', FindingKind.Feed_Silent,
            action=AlertAction.Slack, action_config={'slack_channel': _slack_channel})

        _ = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-slack', utcnow())

        channel, text = recorder.slack_messages[0]

        assert channel == _slack_channel
        assert text == 'Feed on `hl7.test.channel` silent for 400s\n/zato/hl7/channels/'

# ################################################################################################################################

    def test_the_teams_action_sends_html_to_the_rule_target(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('teams-ops', FindingKind.Feed_Silent,
            action=AlertAction.Teams, action_config={'teams_to': _teams_to})

        _ = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-teams', utcnow())

        to, html = recorder.teams_messages[0]

        assert to == _teams_to
        assert html == 'Feed on `hl7.test.channel` silent for 400s<br/><br/>/zato/hl7/channels/'

# ################################################################################################################################

    def test_a_slack_rule_without_a_channel_sends_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('slack-nowhere', FindingKind.Feed_Silent, action=AlertAction.Slack)

        result = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-slack-nowhere', utcnow())

        # The alert itself is still raised, only the delivery is skipped
        assert result.raised_count == 1
        assert recorder.slack_messages == []

# ################################################################################################################################

    def test_a_teams_rule_without_a_target_sends_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('teams-nowhere', FindingKind.Feed_Silent, action=AlertAction.Teams)

        result = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-teams-nowhere', utcnow())

        # The alert itself is still raised, only the delivery is skipped
        assert result.raised_count == 1
        assert recorder.teams_messages == []

# ################################################################################################################################
# ################################################################################################################################

class TestDefaultTargets:
    """ A rule whose action config names no target of its own delivers through
    the deployment-level defaults from the sweep job's extra.
    """

    def test_a_webhook_rule_without_a_url_uses_the_default_one(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('webhook-default', FindingKind.Feed_Silent, action=AlertAction.Webhook)

        defaults = AlertDefaults()
        defaults.webhook_url = _webhook_url

        _ = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-webhook-default', utcnow(),
            defaults=defaults)

        url, payload = recorder.posts[0]

        # The webhook carries the whole structured payload, rendered by its template
        assert url == _webhook_url
        assert payload['rule'] == 'webhook-default'
        assert payload['kind'] == FindingKind.Feed_Silent
        assert payload['object_name'] == _channel_name
        assert payload['message'] == 'Feed on `hl7.test.channel` silent for 400s'
        assert payload['link'] == '/zato/hl7/channels/'
        assert payload['severity'] == AlertSeverity.Warning
        assert payload['count'] == 1
        assert payload['action_config'] == {}
        assert isinstance(payload['alert_id'], int)

# ################################################################################################################################

    def test_a_rule_with_its_own_webhook_ignores_the_defaults(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        own_url = 'https://example.atlassian.net/automation/webhooks/own-rule'

        rule = new_rule('webhook-own', FindingKind.Feed_Silent,
            action=AlertAction.Webhook, action_config={'webhook_url': own_url})

        defaults = AlertDefaults()
        defaults.webhook_url = _webhook_url

        _ = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-webhook-own', utcnow(),
            defaults=defaults)

        url, _ignored = recorder.posts[0]

        assert url == own_url

# ################################################################################################################################

    def test_a_webhook_rule_with_no_url_anywhere_sends_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        rule = new_rule('webhook-nowhere', FindingKind.Feed_Silent, action=AlertAction.Webhook)

        result = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-webhook-nowhere', utcnow())

        # The alert itself is still raised, only the delivery is skipped
        assert result.raised_count == 1
        assert recorder.posts == []

# ################################################################################################################################
# ################################################################################################################################

class TestDedupAndCriticalFloor:

    def test_a_repetition_is_not_dispatched_but_is_still_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()
        transports = recorder.make()
        now = utcnow()

        rule = new_rule('slack-ops', FindingKind.Feed_Silent,
            action=AlertAction.Slack, action_config={'slack_channel': _slack_channel})

        first = process_findings([rule], [_new_finding()], transports, audit_log, 'cid-quiet-1', now)
        second = process_findings([rule], [_new_finding()], transports, audit_log, 'cid-quiet-2', now)

        # The repetition was deduplicated and not dispatched again ..
        assert first.raised_count == 1
        assert second.raised_count == 0
        assert second.deduplicated_count == 1
        assert len(recorder.slack_messages) == 1

        # .. yet both occurrences are in the audit trail, the second with its count.
        assert _count_alert_events() == 2

# ################################################################################################################################

    def test_a_critical_finding_is_never_suppressed(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()
        transports = recorder.make()
        now = utcnow()

        rule = new_rule('slack-ops', FindingKind.Feed_Silent,
            action=AlertAction.Slack, action_config={'slack_channel': _slack_channel})

        critical = _new_finding(severity=AlertSeverity.Critical)

        _ = process_findings([rule], [critical], transports, audit_log, 'cid-critical-1', now)
        second = process_findings([rule], [critical], transports, audit_log, 'cid-critical-2', now)

        # Deduplicated in the store - dispatched anyway, with the count prefix
        assert second.deduplicated_count == 1
        assert len(recorder.slack_messages) == 2

        _, text = recorder.slack_messages[1]
        assert text.startswith('[2x] ')

# ################################################################################################################################
# ################################################################################################################################

class TestDefaultSink:

    def test_an_unmatched_finding_never_vanishes(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        # The one rule cares about a different kind
        rule = new_rule('error-rates', FindingKind.Error_Rate,
            action=AlertAction.Slack, action_config={'slack_channel': _slack_channel})

        result = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-sink', utcnow())

        assert result.raised_count == 0
        assert len(result.unmatched) == 1
        assert recorder.slack_messages == []

# ################################################################################################################################

    def test_the_catch_all_digest_goes_to_the_default_address(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        result = process_findings([], [_new_finding()], recorder.make(), audit_log, 'cid-catch-all', utcnow(),
            defaults=_email_defaults(), dashboard_url='https://dashboard.example.com')

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
            action=AlertAction.Slack, action_config={'slack_channel': _slack_channel})

        _ = process_findings([rule], [_new_finding()], recorder.make(), audit_log, 'cid-trail', utcnow())

        engine = get_audit_engine()

        query = select(event_table).where(event_table.c.event_type == AuditEvent.Alert_Raised)

        with engine.connect() as connection:
            rows = connection.execute(query).fetchall()

        assert len(rows) == 1

        first_row = rows[0]
        row = dict(first_row._mapping)

        assert row['source'] == AuditSource.MLLP_Channel
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
            action=AlertAction.Slack, action_config={'slack_channel': _slack_channel})
        teams_rule = new_rule('teams-ops', FindingKind.Feed_Silent,
            action=AlertAction.Teams, action_config={'teams_to': _teams_to})

        result = process_findings([slack_rule, teams_rule], [_new_finding()], recorder.make(),
            audit_log, 'cid-both', utcnow())

        assert result.raised_count == 2
        assert len(recorder.slack_messages) == 1
        assert len(recorder.teams_messages) == 1
        assert _count_alert_events() == 2

# ################################################################################################################################

    def test_a_transport_that_raises_costs_only_its_own_notification(self) -> 'None':
        audit_log = AuditLog(_server_name)
        recorder = _TransportRecorder()

        # The first delivery of the run fails, the next one goes out as usual
        recorder.slack_failures_left = 1

        first_rule = new_rule('slack-ops', FindingKind.Feed_Silent,
            action=AlertAction.Slack, action_config={'slack_channel': _slack_channel})
        second_rule = new_rule('slack-support', FindingKind.Feed_Silent,
            action=AlertAction.Slack, action_config={'slack_channel': _slack_channel})

        result = process_findings([first_rule, second_rule], [_new_finding()], recorder.make(),
            audit_log, 'cid-transport-error', utcnow())

        # Only the delivery that succeeded counts as dispatched ..
        assert result.dispatched == [('slack-support', AlertAction.Slack)]
        assert len(recorder.slack_messages) == 1

        # .. while both alerts are raised and both are in the audit trail.
        assert result.raised_count == 2
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
