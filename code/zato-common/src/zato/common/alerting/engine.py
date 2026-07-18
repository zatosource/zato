# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alerting engine - findings are routed through the rules that match them,
# deduplicated in the store and dispatched through each rule's action. The transports
# are injected callables, so the engine stays pure and offline-testable - the service
# layer provides the real SMTP, service invoker, pub/sub and HTTP implementations.
# Findings no rule matches go to the default sink - logged and offered as a catch-all
# digest, never dropped - and critical findings are dispatched on every occurrence,
# regardless of dedup and digest settings.

from __future__ import annotations

# stdlib
import logging
from dataclasses import dataclass
from datetime import datetime

# Zato
from zato.common.alerting.model import rule_matches, AlertAction, AlertSeverity
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

    # http_post(url, payload_dict) - what the Slack and Teams webhooks ride on
    http_post: 'callable_' = None

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

def build_slack_payload(message:'str', link:'str') -> 'stranydict':
    """ Builds the body of one Slack incoming-webhook post.
    """
    text = message

    if link:
        text = f'{message}\n{link}'

    out = {'text': text}
    return out

# ################################################################################################################################

def build_teams_payload(message:'str', link:'str', severity:'str') -> 'stranydict':
    """ Builds the body of one Teams incoming-webhook post - a message card
    colored by severity.
    """
    text = message

    if link:
        text = f'{message}\n\n{link}'

    out = {
        '@type': 'MessageCard',
        '@context': 'https://schema.org/extensions',
        'summary': message,
        'themeColor': _teams_theme_colors[severity],
        'title': _teams_card_title,
        'text': text,
    }

    return out

# ################################################################################################################################

def build_alert_payload(rule:'AlertRule', finding:'Finding', alert_id:'int', count:'int') -> 'stranydict':
    """ Builds the structured payload the invoke-service and publish-to-topic actions
    carry - everything an automated remediation needs to act on the alert.
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
    }

    return out

# ################################################################################################################################

def dispatch_action(
    rule:'AlertRule',
    finding:'Finding',
    alert_id:'int',
    count:'int',
    transports:'AlertTransports',
    ) -> 'None':
    """ Runs one rule's action for one alert - the rendered message goes out
    through whichever transport the rule chose.
    """
    message = render_alert_message(count, finding.message)

    if rule.action == AlertAction.Email_Digest:
        addresses = rule.action_config['addresses']
        transports.send_email(addresses, message, f'{message}\n{finding.link}')

    elif rule.action == AlertAction.Invoke_Service:
        service_name = rule.action_config['service']
        payload = build_alert_payload(rule, finding, alert_id, count)
        transports.invoke_service(service_name, payload)

    elif rule.action == AlertAction.Publish_To_Topic:
        topic_name = rule.action_config['topic']
        payload = build_alert_payload(rule, finding, alert_id, count)
        transports.publish(topic_name, payload)

    elif rule.action == AlertAction.Slack:
        webhook_url = rule.action_config['webhook_url']
        payload = build_slack_payload(message, finding.link)
        transports.http_post(webhook_url, payload)

    elif rule.action == AlertAction.Teams:
        webhook_url = rule.action_config['webhook_url']
        payload = build_teams_payload(message, finding.link, finding.severity)
        transports.http_post(webhook_url, payload)

# ################################################################################################################################

def build_digest(findings:'finding_list', *, dashboard_url:'str'='') -> 'strtuple':
    """ Turns findings into the subject and body of one digest email,
    one line per finding, each linking to its Dashboard page.
    """
    count = len(findings)
    suffix = 'finding' if count == 1 else 'findings'

    subject = f'Zato alert digest - {count} {suffix}'

    lines = []

    for finding in findings:
        link = f'{dashboard_url}{finding.link}'
        lines.append(f'* {finding.message}\n  {link}')

    body = '\n\n'.join(lines)

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
    default_email:'strlist | None' = None,
    dashboard_url:'str' = '',
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

    # Our response to produce - the fields are assigned here because init=False
    # means the field factories never run
    out = ProcessResult()
    out.dispatched = []
    out.unmatched = []

    for finding in findings:

        matched_rules = [rule for rule in rules if rule_matches(rule, finding)]

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
                dispatch_action(rule, finding, raise_result.alert_id, raise_result.count, transports)
                out.dispatched.append((rule.name, rule.action))

    # The default sink emails its catch-all digest when an address is configured
    if out.unmatched and default_email:
        subject, body = build_digest(out.unmatched, dashboard_url=dashboard_url)
        transports.send_email(default_email, subject, body)

    return out

# ################################################################################################################################
# ################################################################################################################################
