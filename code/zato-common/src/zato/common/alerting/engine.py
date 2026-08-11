# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alerting engine - findings are routed through the rules that match them,
# deduplicated in the store and dispatched through each rule's action. The transports
# are injected callables, so the engine stays pure and offline-testable - the service
# layer provides the real SMTP, service invoker, pub/sub and HTTP implementations.
# What each notification says comes from the Jinja templates on disk, and a rule
# whose action config names no target of its own delivers through the deployment-level
# defaults from the sweep job's extra. Findings no rule matches go to the default
# sink - logged and offered as a catch-all digest, never dropped - and critical
# findings are dispatched on every occurrence, regardless of dedup and digest settings.

from __future__ import annotations

# stdlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime

# Zato
from zato.common.alerting.model import rule_matches, AlertAction, AlertSeverity
from zato.common.alerting.rendering import render_alert_template, Template_Digest_Body, Template_Digest_Subject, \
    Template_Email_Body, Template_Email_Subject, Template_Slack, Template_Teams, Template_Webhook
from zato.common.alerting.store import raise_alert, render_alert_message
from zato.common.audit_log.api import AuditEvent, get_audit_engine
from zato.common.json_internal import dumps
from zato.common.typing_ import list_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.alerting.model import finding_list, rule_list, AlertRule, Finding
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import anylist, callable_, stranydict, strlist, strtuple
    AlertRule = AlertRule
    anylist = anylist
    AuditLog = AuditLog
    callable_ = callable_
    finding_list = finding_list
    Finding = Finding
    rule_list = rule_list
    stranydict = stranydict
    strlist = strlist
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# The Teams message card colors per severity, hex without the hash sign.
_teams_theme_colors = {
    AlertSeverity.Info:     '0076d7',
    AlertSeverity.Warning:  'e8a317',
    AlertSeverity.Critical: 'cc0000',
}

# The title Teams cards are posted under.
_teams_card_title = 'Zato alert'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AlertTransports:
    """ The delivery callables behind the action menu, injected by the service layer -
    the engine decides what to dispatch, the transports perform the delivery.
    """

    # send_email(addresses, subject, body)
    send_email: 'callable_' = None

    # invoke_service(service_name, payload_dict)
    invoke_service: 'callable_' = None

    # publish(topic_name, payload_dict)
    publish: 'callable_' = None

    # http_post(url, payload_dict) - what the Slack, Teams and plain webhooks ride on
    http_post: 'callable_' = None

# ################################################################################################################################

@dataclass(init=False)
class AlertDefaults:
    """ The deployment-level notification targets - read from the sweep job's extra,
    they answer whenever a rule's own action config names no target, so a seeded
    rule saying only which channel to use delivers without being edited.
    """

    # Where the catch-all digest and target-less email rules deliver
    email_to: 'strlist | None' = None

    # Where target-less Slack rules post
    slack_webhook: str = ''

    # Where target-less Teams rules post
    teams_webhook: str = ''

    # Where target-less plain webhook rules post - e.g. a Jira automation webhook
    webhook_url: str = ''

# ################################################################################################################################

@dataclass(init=False)
class ProcessResult:
    """ The outcome of one engine run.
    """
    raised_count: int = 0
    deduplicated_count: int = 0

    # One entry per dispatched action - (rule name, action)
    dispatched: 'anylist' = list_field()

    # The findings no rule matched - the default sink's input
    unmatched: 'anylist' = list_field()

# ################################################################################################################################
# ################################################################################################################################

def build_template_context(rule:'AlertRule', finding:'Finding', alert_id:'int', count:'int') -> 'stranydict':
    """ The context every notification template renders with - the alert as one dict,
    the rendered message with its repetition prefix included. The diagnosis keys are
    empty here because a diagnosis, when there is one, is attached by the diagnosis
    service, which renders through the same templates with these keys filled in.
    """
    message = render_alert_message(count, finding.message)

    out = {
        'alert_id': alert_id,
        'rule': rule.name,
        'kind': finding.kind,
        'source': finding.source,
        'object_name': finding.object_name,
        'message': message,
        'link': finding.link,
        'severity': finding.severity,
        'count': count,
        'action_config': rule.action_config,
        'diagnosis': '',
        'confidence': '',
        'remediation': None,
    }

    return out

# ################################################################################################################################

def build_slack_payload(text:'str') -> 'stranydict':
    """ Wraps one rendered Slack text in the incoming-webhook envelope -
    the text itself comes from the slack template.
    """
    out = {'text': text}
    return out

# ################################################################################################################################

def build_teams_payload(text:'str', summary:'str', severity:'str') -> 'stranydict':
    """ Wraps one rendered Teams text in the message-card envelope, colored
    by severity - the text itself comes from the teams template.
    """
    out = {
        '@type': 'MessageCard',
        '@context': 'https://schema.org/extensions',
        'summary': summary,
        'themeColor': _teams_theme_colors[severity],
        'title': _teams_card_title,
        'text': text,
    }

    return out

# ################################################################################################################################

def build_alert_payload(rule:'AlertRule', finding:'Finding', alert_id:'int', count:'int') -> 'stranydict':
    """ Builds the structured payload the invoke-service and publish-to-topic actions
    carry - everything an automated remediation needs to act on the alert, the rule's
    own action configuration included, so the target can read its settings from the rule.
    """
    out = {
        'alert_id': alert_id,
        'rule': rule.name,
        'kind': finding.kind,
        'source': finding.source,
        'object_name': finding.object_name,
        'message': finding.message,
        'link': finding.link,
        'severity': finding.severity,
        'count': count,
        'action_config': rule.action_config,
    }

    return out

# ################################################################################################################################

def _get_webhook_target(rule:'AlertRule', default_url:'str') -> 'str':
    """ The URL one webhook-riding action posts to - the rule's own when it names one,
    the deployment-level default otherwise, empty when neither exists.
    """
    if url := rule.action_config.get('webhook_url'):
        out = url
    else:
        out = default_url

    return out

# ################################################################################################################################

def dispatch_action(
    rule:'AlertRule',
    finding:'Finding',
    alert_id:'int',
    count:'int',
    transports:'AlertTransports',
    defaults:'AlertDefaults | None' = None,
    template_dir:'str' = '',
    ) -> 'None':
    """ Runs one rule's action for one alert - what goes out is rendered from the
    alert templates and delivered through whichever transport the rule chose.
    A rule whose action config names no target of its own uses the
    deployment-level defaults, so a seeded rule saying only which channel
    to use delivers without being edited.
    """
    if defaults is None:
        defaults = AlertDefaults()

    context = build_template_context(rule, finding, alert_id, count)
    message = context['message']

    if rule.action == AlertAction.Email_Digest:

        # A rule without its own address list sends to the sweep's default address
        if not (addresses := rule.action_config.get('addresses')):
            addresses = defaults.email_to

        # With no addresses configured anywhere there is nowhere to send the email
        if not addresses:
            logger.warning(
                'Alert rule `%s` has no addresses and no default email is configured - skipping an email about `%s`',
                rule.name, finding.object_name)
            return

        subject = render_alert_template(Template_Email_Subject, context, template_dir)
        body = render_alert_template(Template_Email_Body, context, template_dir)

        transports.send_email(addresses, subject, body)

    elif rule.action == AlertAction.Invoke_Service:
        service_name = rule.action_config['service']
        payload = build_alert_payload(rule, finding, alert_id, count)
        transports.invoke_service(service_name, payload)

    elif rule.action == AlertAction.Publish_To_Topic:
        topic_name = rule.action_config['topic']
        payload = build_alert_payload(rule, finding, alert_id, count)
        transports.publish(topic_name, payload)

    elif rule.action == AlertAction.Slack:

        webhook_url = _get_webhook_target(rule, defaults.slack_webhook)

        if not webhook_url:
            logger.warning('Alert rule `%s` has no Slack webhook and no default one is configured - skipping `%s`',
                rule.name, finding.object_name)
            return

        text = render_alert_template(Template_Slack, context, template_dir)
        payload = build_slack_payload(text)
        transports.http_post(webhook_url, payload)

    elif rule.action == AlertAction.Teams:

        webhook_url = _get_webhook_target(rule, defaults.teams_webhook)

        if not webhook_url:
            logger.warning('Alert rule `%s` has no Teams webhook and no default one is configured - skipping `%s`',
                rule.name, finding.object_name)
            return

        text = render_alert_template(Template_Teams, context, template_dir)
        payload = build_teams_payload(text, message, finding.severity)
        transports.http_post(webhook_url, payload)

    elif rule.action == AlertAction.Webhook:

        webhook_url = _get_webhook_target(rule, defaults.webhook_url)

        if not webhook_url:
            logger.warning('Alert rule `%s` has no webhook URL and no default one is configured - skipping `%s`',
                rule.name, finding.object_name)
            return

        # The webhook template renders the entire JSON body, so shaping the payload
        # for a workflow backend is a template edit, not a code change.
        rendered = render_alert_template(Template_Webhook, context, template_dir)
        payload = json.loads(rendered)
        transports.http_post(webhook_url, payload)

# ################################################################################################################################

def build_digest(findings:'finding_list', *, dashboard_url:'str'='', template_dir:'str'='') -> 'strtuple':
    """ Turns findings into the subject and body of one digest email,
    one entry per finding, each linking to its Dashboard page - both
    rendered from the digest templates.
    """
    entries = []

    for finding in findings:
        entries.append({
            'message': finding.message,
            'link': f'{dashboard_url}{finding.link}',
        })

    context = {
        'count': len(findings),
        'findings': entries,
    }

    subject = render_alert_template(Template_Digest_Subject, context, template_dir)
    body = render_alert_template(Template_Digest_Body, context, template_dir)

    out = subject, body
    return out

# ################################################################################################################################

def record_alert_event(audit_log:'AuditLog', rule:'AlertRule', finding:'Finding', count:'int', cid:'str') -> 'None':
    """ Writes one alert occurrence as an alert-raised audit event, filed under
    the object it is about, so reports can count alerting history per object.
    """
    details = {
        'kind': finding.kind,
        'message': finding.message,
        'rule': rule.name,
        'count': count,
    }

    _ = audit_log.insert(finding.source, AuditEvent.Alert_Raised, finding.object_name, cid=cid, data=dumps(details))

# ################################################################################################################################
# ################################################################################################################################

def process_findings(
    rules:'rule_list',
    findings:'finding_list',
    transports:'AlertTransports',
    audit_log:'AuditLog',
    cid:'str',
    now:'datetime',
    *,
    defaults:'AlertDefaults | None' = None,
    dashboard_url:'str' = '',
    template_dir:'str' = '',
    ) -> 'ProcessResult':
    """ Runs the engine once - every finding is routed through every rule that matches it,
    deduplicated in the store and dispatched through the rule's action. A repetition
    within the dedup window increments the count without being dispatched again,
    unless the finding is critical - critical findings are dispatched on every
    occurrence and can never be suppressed. Findings no rule matches go to the
    default sink: logged, returned, and emailed as a catch-all digest
    when a default address is configured.
    """
    engine = get_audit_engine()

    if defaults is None:
        defaults = AlertDefaults()

    # Our response to produce - the fields are assigned here because init=False
    # means the field factories never run
    out = ProcessResult()
    out.dispatched = []
    out.unmatched = []

    for finding in findings:

        matched_rules = []

        for rule in rules:
            if rule_matches(rule, finding):
                matched_rules.append(rule)

        # No rule matched - the finding goes to the default sink instead of being dropped
        if not matched_rules:
            logger.warning('No alert rule matched finding `%s` on `%s` - %s',
                finding.kind, finding.object_name, finding.message)
            out.unmatched.append(finding)
            continue

        for rule in matched_rules:

            raise_result = raise_alert(engine, rule, finding, now)

            if raise_result.is_new:
                out.raised_count += 1
            else:
                out.deduplicated_count += 1

            # Every occurrence lands in the audit trail, deduplicated or not
            record_alert_event(audit_log, rule, finding, raise_result.count, cid)

            # A repetition within the window is not dispatched again - unless
            # the finding is critical, which is never suppressed
            if raise_result.is_new or finding.severity == AlertSeverity.Critical:
                dispatch_action(rule, finding, raise_result.alert_id, raise_result.count, transports, defaults, template_dir)
                out.dispatched.append((rule.name, rule.action))

    # The default sink emails its catch-all digest when an address is configured
    if out.unmatched and defaults.email_to:
        subject, body = build_digest(out.unmatched, dashboard_url=dashboard_url, template_dir=template_dir)
        transports.send_email(defaults.email_to, subject, body)

    return out

# ################################################################################################################################
# ################################################################################################################################
