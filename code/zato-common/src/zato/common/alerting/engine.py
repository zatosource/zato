# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alerting engine - findings are routed through the rules that match them,
# deduplicated in the store and dispatched through each rule's action. The transports
# are injected callables - the service layer provides the real SMTP, Slack and Microsoft
# Teams connections, the service invoker, pub/sub and HTTP for plain webhooks. Email,
# Slack and Teams deliver through the connections that share the default notification
# name, and a rule only says where within them, e.g. which Slack channel. What each
# notification says comes from the Jinja templates on disk. Findings no rule matches
# go to the default sink - logged and offered as a catch-all digest - and critical
# findings are dispatched on every occurrence, regardless of dedup and digest settings.

from __future__ import annotations

# stdlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from traceback import format_exc

# Zato
from zato.common.alerting.model import rule_matches, AlertAction, AlertSeverity
from zato.common.alerting.rendering import render_alert_template, Template_Digest_Body, Template_Digest_Subject, \
    Template_Email_Body, Template_Email_Subject, Template_Slack, Template_Teams, Template_Webhook
from zato.common.alerting.store import raise_alert, render_alert_message
from zato.common.api import Incidents
from zato.common.audit_log.api import AuditEvent, get_audit_engine
from zato.common.json_internal import dumps
from zato.common.typing_ import list_field
from zato.common.util.api import pluralize

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

@dataclass(init=False)
class AlertTransports:
    """ The delivery callables behind the action menu, injected by the service layer -
    the engine decides what to dispatch, the transports perform the delivery.
    The email, Slack and Teams callables deliver through the connections that share
    the default notification name, and each of them skips quietly when its connection
    does not exist or is inactive.
    """

    # send_email(addresses, subject, body)
    send_email: 'callable_' = None

    # invoke_service(service_name, payload_dict)
    invoke_service: 'callable_' = None

    # publish(topic_name, payload_dict)
    publish: 'callable_' = None

    # send_slack(channel, text)
    send_slack: 'callable_' = None

    # send_teams(to, html)
    send_teams: 'callable_' = None

    # http_post(url, payload_dict) - what the plain webhook action rides on
    http_post: 'callable_' = None

# ################################################################################################################################

@dataclass(init=False)
class AlertDefaults:
    """ The deployment-level notification targets - read from the sweep job's extra,
    they answer whenever a rule's own action config names no target.
    """

    # Where the catch-all digest and target-less email rules deliver
    email_to: 'strlist | None' = None

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
    empty here - the diagnosis service fills them in when it renders through
    the same templates.
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

def build_alert_payload(rule:'AlertRule', finding:'Finding', alert_id:'int', count:'int') -> 'stranydict':
    """ Builds the structured payload the invoke-service and publish-to-topic actions
    carry - everything an automated remediation needs to act on the alert, the rule's
    own action configuration included.
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

def _dispatch_email(
    rule:'AlertRule',
    finding:'Finding',
    context:'stranydict',
    alert_id:'int',
    count:'int',
    transports:'AlertTransports',
    defaults:'AlertDefaults',
    template_dir:'str',
    ) -> 'None':
    """ Sends one alert as an email to the rule's own addresses, or to the sweep's
    default ones when the rule names none.
    """

    # A rule without its own address list sends to the sweep's default address.
    if not (addresses := rule.action_config.get('addresses')):
        addresses = defaults.email_to

    # With no addresses configured anywhere there is nowhere to send the email.
    if not addresses:
        logger.warning(
            'Alert rule `%s` has no addresses and no default email is configured - skipping an email about `%s`',
            rule.name, finding.object_name)
        return

    subject = render_alert_template(Template_Email_Subject, context, template_dir)
    body = render_alert_template(Template_Email_Body, context, template_dir)

    transports.send_email(addresses, subject, body)

# ################################################################################################################################

def _dispatch_invoke_service(
    rule:'AlertRule',
    finding:'Finding',
    context:'stranydict',
    alert_id:'int',
    count:'int',
    transports:'AlertTransports',
    defaults:'AlertDefaults',
    template_dir:'str',
    ) -> 'None':
    """ Invokes the service the rule names, handing it the alert's structured payload.
    """
    service_name = rule.action_config['service']
    payload = build_alert_payload(rule, finding, alert_id, count)

    transports.invoke_service(service_name, payload)

# ################################################################################################################################

def _dispatch_publish(
    rule:'AlertRule',
    finding:'Finding',
    context:'stranydict',
    alert_id:'int',
    count:'int',
    transports:'AlertTransports',
    defaults:'AlertDefaults',
    template_dir:'str',
    ) -> 'None':
    """ Publishes the alert's structured payload to the topic the rule names.
    """
    topic_name = rule.action_config['topic']
    payload = build_alert_payload(rule, finding, alert_id, count)

    transports.publish(topic_name, payload)

# ################################################################################################################################

def _dispatch_slack(
    rule:'AlertRule',
    finding:'Finding',
    context:'stranydict',
    alert_id:'int',
    count:'int',
    transports:'AlertTransports',
    defaults:'AlertDefaults',
    template_dir:'str',
    ) -> 'None':
    """ Posts one alert to the Slack channel the rule names.
    """

    # Without a channel in the rule's action config there is nowhere to post.
    if not (channel := rule.action_config.get(Incidents.Config_Slack_Channel)):
        logger.warning('Alert rule `%s` has no Slack channel - skipping `%s`', rule.name, finding.object_name)
        return

    text = render_alert_template(Template_Slack, context, template_dir)

    transports.send_slack(channel, text)

# ################################################################################################################################

def _dispatch_teams(
    rule:'AlertRule',
    finding:'Finding',
    context:'stranydict',
    alert_id:'int',
    count:'int',
    transports:'AlertTransports',
    defaults:'AlertDefaults',
    template_dir:'str',
    ) -> 'None':
    """ Posts one alert to the Microsoft Teams target the rule names.
    """

    # Without a target in the rule's action config there is nowhere to post.
    if not (to := rule.action_config.get(Incidents.Config_Teams_To)):
        logger.warning('Alert rule `%s` has no Teams target - skipping `%s`', rule.name, finding.object_name)
        return

    # Teams messages are HTML.
    text = render_alert_template(Template_Teams, context, template_dir)
    html = text.replace('\n', '<br/>')

    transports.send_teams(to, html)

# ################################################################################################################################

def _dispatch_webhook(
    rule:'AlertRule',
    finding:'Finding',
    context:'stranydict',
    alert_id:'int',
    count:'int',
    transports:'AlertTransports',
    defaults:'AlertDefaults',
    template_dir:'str',
    ) -> 'None':
    """ Posts one alert to the rule's webhook URL, or to the deployment-level one
    when the rule names none.
    """
    webhook_url = _get_webhook_target(rule, defaults.webhook_url)

    if not webhook_url:
        logger.warning('Alert rule `%s` has no webhook URL and no default one is configured - skipping `%s`',
            rule.name, finding.object_name)
        return

    # The webhook template renders the entire JSON body, so the payload a workflow
    # backend expects is a matter of the template alone.
    rendered = render_alert_template(Template_Webhook, context, template_dir)
    payload = json.loads(rendered)

    transports.http_post(webhook_url, payload)

# ################################################################################################################################

# Which function delivers each action.
_dispatchers = {
    AlertAction.Email_Digest:     _dispatch_email,
    AlertAction.Invoke_Service:   _dispatch_invoke_service,
    AlertAction.Publish_To_Topic: _dispatch_publish,
    AlertAction.Slack:            _dispatch_slack,
    AlertAction.Teams:            _dispatch_teams,
    AlertAction.Webhook:          _dispatch_webhook,
}

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
    Email, Slack and Teams ride on the connections behind their transports,
    and a rule whose action config names no address list or webhook URL of its own
    uses the deployment-level defaults.
    """
    if defaults is None:
        defaults = AlertDefaults()

    context = build_template_context(rule, finding, alert_id, count)

    if dispatcher := _dispatchers.get(rule.action):
        dispatcher(rule, finding, context, alert_id, count, transports, defaults, template_dir)

    # .. anything else is an action no transport delivers.
    else:
        logger.warning('Alert rule `%s` names action `%s` that nothing delivers - skipping `%s`',
            rule.name, rule.action, finding.object_name)

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

    data = dumps(details)

    _ = audit_log.insert(finding.source, AuditEvent.Alert_Raised, finding.object_name, cid=cid, data=data)

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
    when a default address is configured. A transport that raises costs its own
    notification only - the alert is already raised and in the audit trail,
    and the findings after it are dispatched as usual.
    """
    engine = get_audit_engine()

    if defaults is None:
        defaults = AlertDefaults()

    # Our response to produce - the fields are assigned here because init=False
    # means the field factories never run.
    out = ProcessResult()
    out.dispatched = []
    out.unmatched = []

    for finding in findings:

        matched_rules = []

        for rule in rules:
            if rule_matches(rule, finding):
                matched_rules.append(rule)

        # No rule matched - the finding goes to the default sink instead of being dropped.
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

            # Every occurrence lands in the audit trail, deduplicated or not.
            record_alert_event(audit_log, rule, finding, raise_result.count, cid)

            # A repetition within the window is not dispatched again - unless
            # the finding is critical, which is never suppressed.
            if raise_result.is_new or finding.severity == AlertSeverity.Critical:

                # A transport that cannot deliver - an unreachable webhook, an SMTP server
                # that is down - loses this one notification and nothing else.
                try:
                    dispatch_action(rule, finding, raise_result.alert_id, raise_result.count, transports, defaults,
                        template_dir)
                except Exception:
                    logger.warning('Alert rule `%s` could not dispatch %s about `%s` -> %s',
                        rule.name, rule.action, finding.object_name, format_exc())
                else:
                    out.dispatched.append((rule.name, rule.action))

    # The default sink emails its catch-all digest when an address is configured.
    if out.unmatched and defaults.email_to:
        subject, body = build_digest(out.unmatched, dashboard_url=dashboard_url, template_dir=template_dir)

        try:
            transports.send_email(defaults.email_to, subject, body)
        except Exception:
            finding_label = pluralize(len(out.unmatched), 'finding')
            logger.warning('The alert digest of %s could not be sent -> %s', finding_label, format_exc())

    return out

# ################################################################################################################################
# ################################################################################################################################
