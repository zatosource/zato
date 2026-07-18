# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One alerting sweep - the scheduler-driven run that loads the configured rules,
# gives each one to the collector its kind selects and routes the findings through
# the engine. Rules live as generic objects, the same rows enmasse imports and exports,
# so a sweep always runs over the configuration as it currently stands.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from datetime import datetime

# Zato
from zato.common.alerting.collectors import collect_error_rate, collect_feed_silent, collect_missing_followups, \
    collect_outstanding_threshold
from zato.common.alerting.engine import process_findings
from zato.common.alerting.model import new_rule, Default_Dedup_Window_Seconds, AlertAction, FindingKind
from zato.common.api import Audit_Config
from zato.common.audit_log.api import AuditEvent, AuditSource
from zato.common.odb.query.generic import GenericObjectWrapper
from zato.common.typing_ import list_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.alerting.engine import AlertTransports
    from zato.common.alerting.model import finding_list, rule_list, AlertRule
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import anylist, stranydict, strlist

    AlertRule = AlertRule
    AlertTransports = AlertTransports
    anylist = anylist
    AuditLog = AuditLog
    Engine = Engine
    finding_list = finding_list
    rule_list = rule_list
    SASession = SASession
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The audit source a rule runs over when it does not set one - the HL7 collector pack
# is the first consumer of the sweep, so its source is the default.
Default_Source = AuditSource.HL7

# The event types the follow-up collectors pair up when a rule does not name its own -
# sent-not-acked is the canonical absence check.
Default_Begin_Event_Type = AuditEvent.Message_Sent
Default_End_Event_Type   = AuditEvent.Ack_Received

# How long a sent message may wait for its acknowledgment before it counts as missing.
Default_Deadline_Seconds = 300

# How many unacknowledged messages one object may accumulate before the backlog alerts.
Default_Outstanding_Threshold = 100

# The window and share of error outcomes at which an object counts as degraded.
Default_Error_Rate_Window_Seconds = 300
Default_Error_Rate_Threshold = 0.25

# How long a feed may stay silent before it counts as dead.
Default_Silent_After_Seconds = 300

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SweepResult:
    """ The outcome of one alerting sweep.
    """
    rule_count: int = 0
    finding_count: int = 0
    raised_count: int = 0
    deduplicated_count: int = 0

    # One entry per dispatched action - (rule name, action)
    dispatched: 'anylist' = list_field()

# ################################################################################################################################
# ################################################################################################################################

def parse_rule(name:'str', rule_data:'stranydict') -> 'AlertRule':
    """ Builds one rule from its stored form - the dict a generic-object row carries.
    Every field beyond the kind is optional, mirroring the YAML definition.
    """
    out = new_rule(
        name,
        rule_data['kind'],
        source=rule_data.get('source', ''),
        object_name=rule_data.get('object_name', ''),
        action=rule_data.get('action', AlertAction.Email_Digest),
        action_config=rule_data.get('action_config', {}),
        config=rule_data.get('config', {}),
        dedup_window_seconds=rule_data.get('dedup_window_seconds', Default_Dedup_Window_Seconds),
        is_active=rule_data.get('is_active', True),
    )

    return out

# ################################################################################################################################

def load_rules(session:'SASession', cluster_id:'int') -> 'rule_list':
    """ Loads all the alert rules from their generic-object rows - the same rows
    the enmasse importer writes and the exporter reads.
    """

    # Our response to produce
    out:'rule_list' = []

    wrapper = GenericObjectWrapper(session, cluster_id)
    wrapper.type_ = Audit_Config.Type.Alert_Rule

    rows = wrapper.get_list()

    for row in rows:
        rule = parse_rule(row['name'], row)
        out.append(rule)

    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_for_rule(
    engine:'Engine',
    rule:'AlertRule',
    metrics_by_name:'stranydict',
    now:'datetime',
    ) -> 'finding_list':
    """ Runs the collector the rule's kind selects, parameterized by the rule's
    own config - unset parameters fall back to the module-level defaults.
    """
    config = rule.config

    # An unset source means the default collector pack's source
    source = rule.source
    if not source:
        source = Default_Source

    if rule.kind == FindingKind.Missing_Followup:

        out = collect_missing_followups(
            engine,
            source,
            config.get('begin_event_type', Default_Begin_Event_Type),
            config.get('end_event_type', Default_End_Event_Type),
            config.get('deadline_seconds', Default_Deadline_Seconds),
            now,
            object_name=rule.object_name,
            link=config.get('link', ''),
        )

    elif rule.kind == FindingKind.Outstanding:

        out = collect_outstanding_threshold(
            engine,
            source,
            config.get('begin_event_type', Default_Begin_Event_Type),
            config.get('end_event_type', Default_End_Event_Type),
            config.get('threshold', Default_Outstanding_Threshold),
            object_name=rule.object_name,
            link=config.get('link', ''),
        )

    elif rule.kind == FindingKind.Error_Rate:

        out = collect_error_rate(
            engine,
            source,
            config.get('window_seconds', Default_Error_Rate_Window_Seconds),
            config.get('threshold', Default_Error_Rate_Threshold),
            now,
            object_name=rule.object_name,
            link=config.get('link', ''),
        )

    elif rule.kind == FindingKind.Feed_Silent:

        out = collect_feed_silent(
            metrics_by_name,
            source,
            config.get('silent_after_seconds', Default_Silent_After_Seconds),
            link=config.get('link', ''),
        )

    else:
        # A kind with no generic collector produces nothing here - domain packs
        # feed their own findings straight into process_findings instead.
        out = []

    return out

# ################################################################################################################################
# ################################################################################################################################

def run_sweep(
    engine:'Engine',
    rules:'rule_list',
    metrics_by_name:'stranydict',
    transports:'AlertTransports',
    audit_log:'AuditLog',
    cid:'str',
    now:'datetime',
    *,
    default_email:'strlist | None' = None,
    dashboard_url:'str' = '',
    ) -> 'SweepResult':
    """ Runs one full sweep - each active rule's collector runs with the rule's
    own parameters and the findings go through the engine one rule at a time,
    so two rules of the same kind never double-dispatch each other's findings.
    """

    # Our response to produce - the fields are assigned here because init=False
    # means the field factories never run
    out = SweepResult()
    out.dispatched = []

    for rule in rules:

        # An inactive rule's collector does not even run
        if not rule.is_active:
            continue

        out.rule_count += 1

        findings = collect_for_rule(engine, rule, metrics_by_name, now)

        if not findings:
            continue

        out.finding_count += len(findings)

        # The findings were collected for this one rule, so only this one rule
        # processes them - the per-rule narrowing already happened in the collector.
        result = process_findings([rule], findings, transports, audit_log, cid, now,
            default_email=default_email, dashboard_url=dashboard_url)

        out.raised_count += result.raised_count
        out.deduplicated_count += result.deduplicated_count
        out.dispatched.extend(result.dispatched)

    return out

# ################################################################################################################################
# ################################################################################################################################
