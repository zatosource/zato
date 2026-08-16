# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One alerting sweep - the scheduler-driven run that measures the audit database
# and live channel metrics into per-object facts and routes each fact through every
# alert ruleset the rule engine keeps. A rule that fires names its action in its
# `then` outcomes - `outcome.action = 'diagnose'` invokes the diagnosis service,
# with the remaining outcome keys travelling as the action config. Deduplication,
# the audit trace and the dispatch transports all key off the rule that fired.

from __future__ import annotations

# stdlib
import logging
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote

# Zato
from zato.common.alerting.collectors import collect_facts
from zato.common.alerting.engine import process_findings
from zato.common.alerting.model import new_finding, new_rule, AlertAction, AlertSeverity, Default_Dedup_Window_Seconds
from zato.common.api import Alerting, Incidents
from zato.common.audit_log.common import get_source_label, health_sources
from zato.common.defaults import default_cluster_id
from zato.common.rule_engine.loading import documents_from_version, load_documents
from zato.common.typing_ import list_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.alerting.engine import AlertDefaults, AlertTransports
    from zato.common.alerting.model import AlertRule, Finding
    from zato.common.audit_log.api import AuditLog
    from zato.common.rule_engine.models import Rule
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import anylist, stranydict, strintdict, strlist

    AlertDefaults = AlertDefaults
    AlertRule = AlertRule
    AlertTransports = AlertTransports
    anylist = anylist
    AuditLog = AuditLog
    Engine = Engine
    Finding = Finding
    Rule = Rule
    RuleSQLBackend = RuleSQLBackend
    stranydict = stranydict
    strintdict = strintdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
rule_engine_rule_list = list['Rule']

# The entity every fact travels under - rules read `alert.error_rate` and friends.
Fact_Entity = 'alert'

# The prefix a rule's then targets carry - `outcome.action`, `outcome.severity` and so on.
Outcome_Prefix = 'outcome.'

# What each outcome.action value means in engine terms - `diagnose` is invoke-service
# pointed at the diagnosis service, everything else maps one to one.
_action_by_outcome = {
    'diagnose':         AlertAction.Invoke_Service,
    'email':            AlertAction.Email_Digest,
    'invoke-service':   AlertAction.Invoke_Service,
    'publish-to-topic': AlertAction.Publish_To_Topic,
    'slack':            AlertAction.Slack,
    'teams':            AlertAction.Teams,
    'webhook':          AlertAction.Webhook,
}

# The severities an outcome may carry.
_severities = (AlertSeverity.Info, AlertSeverity.Warning, AlertSeverity.Critical)

# Where a finding's link leads when the rule names none of its own - the audit log page,
# the one existing screen every dashboard URL already wraps in login_required.
Audit_Log_Path = '/zato/audit-log/'

# What the deep link asks the audit log page to do with the failing event.
Resubmit_Action = 'resubmit'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SweepResult:
    """ The outcome of one alerting sweep.
    """
    rule_count: int = 0
    fact_count: int = 0
    finding_count: int = 0
    raised_count: int = 0
    deduplicated_count: int = 0

    # One entry per dispatched action - (rule name, action)
    dispatched: 'anylist' = list_field()

# ################################################################################################################################
# ################################################################################################################################

def is_alert_ruleset(name:'str') -> 'bool':
    """ Whether one ruleset name belongs to alerting - the prefix itself, the name
    of the single ruleset from before the per-type split, or any name led by the
    prefix and an underscore, the way alerts_rest and its siblings are named.
    """
    if name == Alerting.Ruleset_Prefix:
        return True

    out = name.startswith(Alerting.Ruleset_Prefix + '_')
    return out

# ################################################################################################################################

def load_alert_rules(backend:'RuleSQLBackend') -> 'rule_engine_rule_list':
    """ Loads the live versions of every alert ruleset from the rule engine store -
    each ruleset whose name carries the alerts prefix - returning their rules
    in ruleset order, then rule order. No such rulesets or nothing published yet
    means there is nothing to sweep with - an empty list, not an error.
    """

    # Our response to produce
    out:'rule_engine_rule_list' = []

    # Only active rulesets with a live version can be swept with at all
    published = backend.definitions.list_published_rulesets()

    for definition in published:

        # A ruleset outside the alerts prefix is someone else's business
        if not is_alert_ruleset(definition.name):
            continue

        record = backend.versions.get(definition.id, definition.live_version)
        documents = documents_from_version(record)

        loaded = load_documents(documents)

        # Rule full names embed the ruleset name, so rules from many rulesets never collide
        for full_name in loaded.rule_names:
            rule = loaded.manager[full_name]
            out.append(rule)

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_fact_message(rule_name:'str', fact:'stranydict') -> 'str':
    """ One readable line saying which rule fired on which object and what
    the measures were at that moment - only the measures that are non-zero speak.
    """
    parts = []

    source = fact['source']
    source_label = get_source_label(source)

    # A connection's own health check is named in the measure rather than after it,
    # because "the check failed" and "the calls failed" are two different sentences.
    is_health_check = source in health_sources

    if fact['total_count']:
        percent = round(fact['error_rate'] * 100)
        error_part = f'error rate {percent}% ({fact["error_count"]} of {fact["total_count"]}'
        error_part += f' over {fact["window_seconds"]}s)'
        parts.append(error_part)

    if fact['outstanding']:
        parts.append(f'{fact["outstanding"]} outstanding (oldest waiting {fact["oldest_waiting_seconds"]}s)')

    if fact['silent_seconds']:
        parts.append(f'silent for {fact["silent_seconds"]}s')

    if fact['consecutive_failures']:
        if is_health_check:
            failure_count = fact['consecutive_failures']
            times = 'time' if failure_count == 1 else 'times'
            parts.append(f'{source_label} failed {failure_count} {times}')
        else:
            parts.append(f'{fact["consecutive_failures"]} consecutive failure(s)')

    if fact['avg_duration_ms']:
        parts.append(f'average duration {fact["avg_duration_ms"]}ms')

    if fact['auth_failure_count']:
        parts.append(f'{fact["auth_failure_count"]} authentication failure(s)')

    if fact['cert_days_left']:
        parts.append(f'certificate expires in {fact["cert_days_left"]} day(s)')

    if fact['health_state']:
        parts.append(f'reported health state `{fact["health_state"]}`')

    if fact['test_transfer_failed']:
        parts.append('the test transfer check failed')

    if fact['start_delay_ms']:
        parts.append(f'started {fact["start_delay_ms"]}ms late')

    if fact['overdue_ratio']:
        parts.append(f'{fact["overdue_ratio"]}x its interval since the last run')

    if seconds_since_last_arrival := fact['seconds_since_last_arrival']:
        parts.append(f'no file for {seconds_since_last_arrival}s')

    if arrival_overdue_ratio := fact['arrival_overdue_ratio']:
        parts.append(f'{arrival_overdue_ratio}x its arrival window since the last file')

    measures = ', '.join(parts)

    # A streak measure on a health source already opens with the source's name, so
    # repeating it in parentheses would say the same thing twice in one sentence ..
    if is_health_check:
        if fact['consecutive_failures']:
            out = f'Rule `{rule_name}` matched `{fact["object_name"]}` - {measures}'
            return out

    # .. every other measure reads the same on either stream, so the source is what tells them apart.
    out = f'Rule `{rule_name}` matched `{fact["object_name"]}` ({source_label}) - {measures}'
    return out

# ################################################################################################################################

def build_finding_link(fact:'stranydict') -> 'str':
    """ Where a finding about one fact leads - the audit log page filtered down to
    the failing object, and straight at the newest failing event, its confirmation
    popover ready to open, when that event's type can be resubmitted from that page.
    """
    source = quote(fact['source'])
    object_name = quote(fact['object_name'])

    out = f'{Audit_Log_Path}?source={source}&object_name={object_name}&cluster={default_cluster_id}'

    # A failure the audit log page can send again deep-links at the event itself
    if fact['is_resubmittable'] and fact['last_error_event_id']:
        out += f'&event={fact["last_error_event_id"]}&action={Resubmit_Action}'

    return out

# ################################################################################################################################

def read_outcome(then:'stranydict') -> 'stranydict':
    """ Returns a match's outcome keys with the entity prefix stripped -
    `outcome.action` becomes `action`.
    """

    # Our response to produce
    out:'stranydict' = {}

    for target, value in then.items():
        if target.startswith(Outcome_Prefix):
            name = target[len(Outcome_Prefix):]
            out[name] = value

    return out

# ################################################################################################################################

def build_dispatch(
    rule:'Rule',
    fact:'stranydict',
    outcome:'stranydict',
    dashboard_url:'str' = '',
    ) -> 'tuple[AlertRule, Finding] | None':
    """ Turns one rule match into the pair the engine dispatches - a transient engine rule
    carrying the outcome's action and config, and a finding carrying the fact's measures.
    An outcome without an action names nothing to do, which is an authoring error, not a dispatch.
    """
    action_name = outcome.pop('action', None)

    if action_name not in _action_by_outcome:
        logger.warning('Alert rule `%s` fired with no usable outcome.action (%r) - nothing to dispatch',
            rule.name, action_name)
        return None

    action = _action_by_outcome[action_name]

    # The engine-level knobs travel as outcome keys too - what remains after
    # they are taken out is the action's own config.
    dedup_window_seconds = outcome.pop('dedup_window_seconds', Default_Dedup_Window_Seconds)

    severity = outcome.pop('severity', AlertSeverity.Warning)
    if severity not in _severities:
        severity = AlertSeverity.Warning

    link = outcome.pop('link', '')

    # A rule that names no link of its own points at the audit log page - straight
    # at the failing event when that event can be sent again from that page,
    # at the object's own rows otherwise.
    if not link:
        link = build_finding_link(fact)

    # What a notification carries is a full address - the dashboard the deployment
    # configured, with the page's own path after it.
    if link.startswith('/') and dashboard_url:
        link = dashboard_url.rstrip('/') + link

    # The diagnose action is invoke-service pointed at the diagnosis service ..
    if action_name == 'diagnose':
        outcome['service'] = Incidents.Service_Diagnose

    # .. and an email outcome's addresses arrive as one comma-separated string.
    if addresses := outcome.pop('addresses', None):
        outcome['addresses'] = [item.strip() for item in addresses.split(',')]

    alert_rule = new_rule(
        rule.name,
        rule.name,
        action=action,
        action_config=outcome,
        dedup_window_seconds=dedup_window_seconds,
    )

    message = build_fact_message(rule.name, fact)

    finding = new_finding(rule.name, fact['source'], fact['object_name'], message, link=link, severity=severity)

    out = alert_rule, finding
    return out

# ################################################################################################################################
# ################################################################################################################################

def run_sweep(
    engine:'Engine',
    rules:'rule_engine_rule_list',
    metrics_by_name:'stranydict',
    metrics_source:'str',
    transports:'AlertTransports',
    audit_log:'AuditLog',
    cid:'str',
    now:'datetime',
    *,
    defaults:'AlertDefaults | None' = None,
    dashboard_url:'str' = '',
    template_dir:'str' = '',
    job_intervals:'strintdict | None' = None,
    arrival_windows:'strintdict | None' = None,
    ) -> 'SweepResult':
    """ Runs one full sweep - the fact producers measure everything once, each fact runs
    through each rule of every alert ruleset, and every match is dispatched through
    the engine one at a time, so dedup and the audit trace see each match on its own.
    """

    # Our response to produce - the fields are assigned here because init=False
    # means the field factories never run
    out = SweepResult()
    out.dispatched = []

    facts = collect_facts(engine, metrics_by_name, metrics_source, now, job_intervals=job_intervals,
        arrival_windows=arrival_windows)
    out.fact_count = len(facts)

    for rule in rules:

        # A rule the listing screen deactivated matches nothing while remaining stored
        if rule.document.get('is_active') is False:
            continue

        out.rule_count += 1

        for fact in facts:

            match_result = rule.match({Fact_Entity: fact})

            if not match_result:
                continue

            outcome = read_outcome(match_result.then)
            dispatch = build_dispatch(rule, fact, outcome, dashboard_url)

            if dispatch is None:
                continue

            alert_rule, finding = dispatch
            out.finding_count += 1

            # The finding was built for this one rule, so only this one rule processes it
            result = process_findings([alert_rule], [finding], transports, audit_log, cid, now,
                defaults=defaults, dashboard_url=dashboard_url, template_dir=template_dir)

            out.raised_count += result.raised_count
            out.deduplicated_count += result.deduplicated_count
            out.dispatched.extend(result.dispatched)

    return out

# ################################################################################################################################
# ################################################################################################################################
