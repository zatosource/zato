# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One alerting sweep - the scheduler-driven run that measures the audit database
# and live channel metrics into per-object facts and routes each fact through the
# `alerts` ruleset the rule engine keeps. A rule that fires names its action in its
# `then` outcomes - `outcome.action = 'incident'` invokes the diagnosis service the
# way the invoke-service action always did, with the remaining outcome keys travelling
# as the action config. The dedup store, the audit trace and the dispatch transports
# stay as they were - only the rule representation and the matching changed.

from __future__ import annotations

# stdlib
import logging
from dataclasses import dataclass
from datetime import datetime

# Zato
from zato.common.alerting.collectors import collect_facts
from zato.common.alerting.engine import process_findings
from zato.common.alerting.model import new_finding, new_rule, AlertAction, AlertSeverity, Default_Dedup_Window_Seconds
from zato.common.api import Alerting, Incidents
from zato.common.rule_engine.loading import documents_from_version, load_documents
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset
from zato.common.typing_ import list_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.alerting.engine import AlertTransports
    from zato.common.alerting.model import AlertRule, Finding
    from zato.common.audit_log.api import AuditLog
    from zato.common.rule_engine.models import Rule
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import anylist, stranydict, strlist

    AlertRule = AlertRule
    AlertTransports = AlertTransports
    anylist = anylist
    AuditLog = AuditLog
    Engine = Engine
    Finding = Finding
    Rule = Rule
    RuleSQLBackend = RuleSQLBackend
    stranydict = stranydict
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

# What each outcome.action value means in engine terms - `incident` is invoke-service
# pointed at the diagnosis service, everything else maps one to one.
_action_by_outcome = {
    'incident':         AlertAction.Invoke_Service,
    'email':            AlertAction.Email_Digest,
    'invoke-service':   AlertAction.Invoke_Service,
    'publish-to-topic': AlertAction.Publish_To_Topic,
    'slack':            AlertAction.Slack,
    'teams':            AlertAction.Teams,
}

# The severities an outcome may carry.
_severities = (AlertSeverity.Info, AlertSeverity.Warning, AlertSeverity.Critical)

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

def load_alert_rules(backend:'RuleSQLBackend') -> 'rule_engine_rule_list':
    """ Loads the live version of the `alerts` ruleset from the rule engine store,
    returning its rules in rule order. No such ruleset or no live version yet
    means there is nothing to sweep with - an empty list, not an error.
    """

    # Our response to produce
    out:'rule_engine_rule_list' = []

    matches = backend.definitions.find_by_name(name=Alerting.Ruleset_Name, object_type=Definition_Type_Ruleset)

    # The ruleset comes into being at environment creation - none means nothing is configured yet
    if not matches:
        return out

    definition = matches[0]

    # A ruleset whose live pointer was never set has nothing published to run
    if not definition.live_version:
        return out

    record = backend.versions.get(definition.id, definition.live_version)
    documents = documents_from_version(record)

    loaded = load_documents(documents)

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

    if fact['total_count']:
        percent = round(fact['error_rate'] * 100)
        error_part = f'error rate {percent}% ({fact["error_count"]} of {fact["total_count"]}'
        error_part += f' over {fact["window_seconds"]}s)'
        parts.append(error_part)

    if fact['outstanding']:
        parts.append(f'{fact["outstanding"]} outstanding (oldest waiting {fact["oldest_waiting_seconds"]}s)')

    if fact['silent_seconds']:
        parts.append(f'silent for {fact["silent_seconds"]}s')

    measures = ', '.join(parts)

    out = f'Rule `{rule_name}` matched `{fact["object_name"]}` ({fact["source"]}) - {measures}'
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

def build_dispatch(rule:'Rule', fact:'stranydict', outcome:'stranydict') -> 'tuple[AlertRule, Finding] | None':
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

    # The incident action is invoke-service pointed at the diagnosis service ..
    if action_name == 'incident':
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
    default_email:'strlist | None' = None,
    dashboard_url:'str' = '',
    ) -> 'SweepResult':
    """ Runs one full sweep - the fact producers measure everything once, each fact runs
    through each rule of the alerts ruleset, and every match is dispatched through
    the engine one at a time, so dedup and the audit trace work exactly as before.
    """

    # Our response to produce - the fields are assigned here because init=False
    # means the field factories never run
    out = SweepResult()
    out.dispatched = []

    facts = collect_facts(engine, metrics_by_name, metrics_source, now)
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
            dispatch = build_dispatch(rule, fact, outcome)

            if dispatch is None:
                continue

            alert_rule, finding = dispatch
            out.finding_count += 1

            # The finding was built for this one rule, so only this one rule processes it
            result = process_findings([alert_rule], [finding], transports, audit_log, cid, now,
                default_email=default_email, dashboard_url=dashboard_url)

            out.raised_count += result.raised_count
            out.deduplicated_count += result.deduplicated_count
            out.dispatched.extend(result.dispatched)

    return out

# ################################################################################################################################
# ################################################################################################################################
