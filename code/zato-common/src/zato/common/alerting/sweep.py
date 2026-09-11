# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One alerting sweep - the scheduler-driven run that measures the audit database
# and live channel metrics into per-object facts and routes each fact through every
# alert ruleset the rule engine keeps. A rule that fires names its action in its
# `then` outcomes - `outcome.action = 'email'` sends an email - with the remaining
# outcome keys travelling as the action config, and a ruleset whose documents say
# the LLM explains its alerts has each of them explained before the action delivers
# it. Deduplication, the audit trace and the dispatch transports all key off the rule that fired.

from __future__ import annotations

# stdlib
import logging
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote

# Zato
from zato.common.alerting.collectors import collect_facts
from zato.common.alerting.config_map import read_window_seconds, type_sources, type_to_ruleset, Explain_With_LLM_Key
from zato.common.alerting.engine import process_findings
from zato.common.alerting.model import new_finding, new_rule, AlertAction, AlertSeverity, Default_Dedup_Window_Seconds
from zato.common.alerting.object_config import Email_Connection_Config_Key, LLM_Connection_Config_Key
from zato.common.alerting.object_settings import build_rule_values, build_window_seconds_by_object, get_email_connection, \
    get_llm_connection, get_muted_rule_names, is_object_active
from zato.common.api import Alerting
from zato.common.audit_log.common import get_source_label, health_sources
from zato.common.defaults import default_cluster_id
from zato.common.rule_engine.document import resolve_defaults
from zato.common.rule_engine.loading import documents_from_version, load_documents
from zato.common.rule_engine.references import referenced_terms
from zato.common.typing_ import list_field
from zato.common.util.api import pluralize

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.alerting.engine import AlertDefaults, AlertTransports
    from zato.common.alerting.model import AlertRule, Finding
    from zato.common.audit_log.api import AuditLog
    from zato.common.rule_engine.models import Rule
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import anydict, anylist, stranydict, strintdict, strlist

    AlertDefaults = AlertDefaults
    AlertRule = AlertRule
    AlertTransports = AlertTransports
    anydict = anydict
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

# What each outcome.action value means in engine terms.
_action_by_outcome = {
    'email':            AlertAction.Email_Digest,
    'invoke-service':   AlertAction.Invoke_Service,
    'publish-to-topic': AlertAction.Publish_To_Topic,
    'slack':            AlertAction.Slack,
    'teams':            AlertAction.Teams,
    'webhook':          AlertAction.Webhook,
}

# The severities an outcome may carry.
_severities = (AlertSeverity.Info, AlertSeverity.Warning, AlertSeverity.Error)

# Which alert type each ruleset's rules belong to - the reverse of the config map's table
_type_by_ruleset:'dict[str, str]' = {}

for _type_name, _ruleset_name in type_to_ruleset.items():
    _type_by_ruleset[_ruleset_name] = _type_name

# Where a finding's link leads when the rule names none of its own - the audit log page,
# the one existing screen every dashboard URL already wraps in login_required.
Audit_Log_Path = '/zato/audit-log/'

# What the deep link asks the audit log page to do with the failing event.
Resubmit_Action = 'resubmit'

# The per-object toggle that says whether the LLM explains the object's alerts - the same
# field the ruleset-wide switch stamps on every rule document.
Use_LLM_Field = 'use_llm'

# The fact's keys that name the object rather than measure it - a rule reads them,
# but there is no evidence to collect for them.
_identity_keys = ('source', 'object_name')

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

def build_window_seconds_by_source(rules:'rule_engine_rule_list') -> 'strintdict':
    """ The measuring window of each audit source, read off the window_seconds default of the rules
    of the type that matches on it - a person changes the type's window on the config screen and
    the collectors measure the type's sources over it. A source whose type has no window rule is absent.
    """

    # Our response to produce
    out:'strintdict' = {}

    # The documents of each ruleset, keyed the way the config map reads them
    documents_by_ruleset:'dict[str, stranydict]' = {}

    for rule in rules:
        if rule.ruleset_name not in documents_by_ruleset:
            documents_by_ruleset[rule.ruleset_name] = {}
        documents_by_ruleset[rule.ruleset_name][rule.full_name] = rule.document

    for type_name, sources in type_sources.items():

        ruleset_name = type_to_ruleset[type_name]

        # A type nothing published has no window to speak of
        if ruleset_name not in documents_by_ruleset:
            continue

        window_seconds = read_window_seconds(documents_by_ruleset[ruleset_name], type_name)

        if window_seconds is None:
            continue

        for source in sources:
            out[source] = window_seconds

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

    if failure_count := fact['consecutive_failures']:
        if is_health_check:
            times_label = pluralize(failure_count, 'time')
            parts.append(f'{source_label} failed {times_label}')
        else:
            failure_label = pluralize(failure_count, 'consecutive failure')
            parts.append(failure_label)

    if fact['avg_duration_ms']:
        parts.append(f'average duration {fact["avg_duration_ms"]}ms')

    if auth_failure_count := fact['auth_failure_count']:
        auth_failure_label = pluralize(auth_failure_count, 'authentication failure')
        parts.append(auth_failure_label)

    if cert_days_left := fact['cert_days_left']:
        days_label = pluralize(cert_days_left, 'day')
        parts.append(f'certificate expires in {days_label}')

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

    if expected_files_missing := fact['expected_files_missing']:
        missing_label = pluralize(expected_files_missing, 'expected file')
        parts.append(f'{missing_label} still missing today, {fact["delivered_today"]} delivered')

    if list_failed_streak := fact['list_failed_streak']:
        run_label = pluralize(list_failed_streak, 'run')
        parts.append(f'the newest {run_label} never reached the directory')

    if failed_files_in_window := fact['failed_files_in_window']:
        failed_label = pluralize(failed_files_in_window, 'file')
        runs_label = pluralize(fact['runs_failed_in_window'], 'run')
        parts.append(f'{failed_label} failed across {runs_label}')

    if runs_interrupted_in_window := fact['runs_interrupted_in_window']:
        interrupted_label = pluralize(runs_interrupted_in_window, 'run')
        parts.append(f'{interrupted_label} cut short by a server stop')

    if quarantined_count := fact['quarantined_count']:
        quarantined_label = pluralize(quarantined_count, 'file')
        parts.append(f'{quarantined_label} quarantined')

    if verify_failed_count := fact['verify_failed_count']:
        verify_label = pluralize(verify_failed_count, 'stored file')
        parts.append(f'{verify_label} did not verify')

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

def build_measures(rule:'Rule') -> 'strlist':
    """ The measures of the fact a rule reads - every `alert.` term of its document without the prefix,
    the keys naming the object left out.
    """

    # Our response to produce
    out:'strlist' = []

    prefix = Fact_Entity + '.'

    for term in referenced_terms(rule.document):

        if not term.startswith(prefix):
            continue

        name = term[len(prefix):]

        if name in _identity_keys:
            continue

        out.append(name)

    return out

# ################################################################################################################################

def build_thresholds(rule:'Rule', rule_values:'stranydict') -> 'stranydict':
    """ The thresholds a rule compared against as they were in force for the object -
    the literal defaults of the rule's document with the object's own numbers over them.
    """

    # Our response to produce
    out:'stranydict' = resolve_defaults(rule.document['defaults'])

    for name, value in rule_values.items():
        if name in out:
            out[name] = value

    return out

# ################################################################################################################################

def build_dispatch(
    rule:'Rule',
    fact:'stranydict',
    outcome:'stranydict',
    dashboard_url:'str' = '',
    settings:'stranydict | None' = None,
    rule_values:'stranydict | None' = None,
    ) -> 'tuple[AlertRule, Finding] | None':
    """ Turns one rule match into the pair the engine dispatches - a transient engine rule
    carrying the outcome's action and config, and a finding carrying the fact's measures,
    the thresholds the rule compared against and the measures it read.
    An outcome without an action names nothing to do, which is an authoring error, not a dispatch.
    An object with settings of its own has its email and LLM connections travel in the action
    config, so the actions deliver through them rather than through the default ones, and its
    own Use LLM switch says whether the LLM explains the alert, over the ruleset's answer.
    """
    if settings is None:
        settings = {}

    if rule_values is None:
        rule_values = {}

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

    # An email outcome's addresses arrive as one comma-separated string.
    if addresses := outcome.pop('addresses', None):
        outcome['addresses'] = [item.strip() for item in addresses.split(',')]

    # The object's own email and LLM connections, when it has them
    if settings:

        if email_connection := get_email_connection(settings):
            outcome[Email_Connection_Config_Key] = email_connection

        if llm_connection := get_llm_connection(settings):
            outcome[LLM_Connection_Config_Key] = llm_connection

    # Whether the LLM explains the alert is the object's own answer when it has settings,
    # the ruleset's otherwise, stamped on every rule document - a rule a person wrote
    # by hand without the key is not explained.
    if Use_LLM_Field in settings:
        explain_with_llm = settings[Use_LLM_Field] is True
    else:
        explain_with_llm = rule.document.get(Explain_With_LLM_Key) is True

    alert_rule = new_rule(
        rule.name,
        rule.name,
        action=action,
        action_config=outcome,
        dedup_window_seconds=dedup_window_seconds,
        explain_with_llm=explain_with_llm,
    )

    message = build_fact_message(rule.name, fact)

    finding = new_finding(rule.name, fact['source'], fact['object_name'], message, link=link, severity=severity,
        fact=fact, thresholds=build_thresholds(rule, rule_values), measures=build_measures(rule))

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
    schedule_expectations:'anydict | None' = None,
    object_settings:'anydict | None' = None,
    ) -> 'SweepResult':
    """ Runs one full sweep - the fact producers measure everything once, each fact runs
    through each rule of every alert ruleset, and every match is dispatched through
    the engine one at a time, so dedup and the audit trace see each match on its own.

    The object settings are what each object's Alerts tab stored, by alert type and object name -
    an object that is not active raises nothing, its toggles mute the rules they stand for,
    its numbers stand in for the rules' defaults, it is measured over its own window
    and its alerts leave through its own email connection.
    """

    # Our response to produce - the fields are assigned here because init=False
    # means the field factories never run
    out = SweepResult()
    out.dispatched = []

    if object_settings is None:
        object_settings = {}

    window_seconds_by_source = build_window_seconds_by_source(rules)
    window_seconds_by_object = build_window_seconds_by_object(object_settings, window_seconds_by_source)

    facts = collect_facts(engine, metrics_by_name, metrics_source, now, window_seconds_by_source=window_seconds_by_source,
        window_seconds_by_object=window_seconds_by_object, job_intervals=job_intervals, arrival_windows=arrival_windows,
        schedule_expectations=schedule_expectations)
    out.fact_count = len(facts)

    for rule in rules:

        # A rule the listing screen deactivated matches nothing while remaining stored
        if rule.document.get('is_active') is False:
            continue

        out.rule_count += 1

        # The objects of the rule's own type carry settings, anyone else's are not its business -
        # a ruleset outside the config map's table, e.g. one a person wrote by hand, has none.
        alert_type = ''
        settings_by_object:'anydict' = {}

        if rule.ruleset_name in _type_by_ruleset:
            alert_type = _type_by_ruleset[rule.ruleset_name]

            if alert_type in object_settings:
                settings_by_object = object_settings[alert_type]

        for fact in facts:

            match_data = {Fact_Entity: fact}
            settings:'stranydict' = {}
            rule_values:'stranydict' = {}

            if fact['object_name'] in settings_by_object:

                settings = settings_by_object[fact['object_name']]

                # An object switched off raises nothing at all ..
                if not is_object_active(settings):
                    continue

                # .. one with a toggle off never reaches the rules the toggle stands for ..
                if rule.name in get_muted_rule_names(alert_type, settings):
                    continue

                # .. and its own numbers stand in for the rule's defaults.
                rule_values = build_rule_values(alert_type, settings)
                match_data.update(rule_values)

            match_result = rule.match(match_data)

            if not match_result:
                continue

            outcome = read_outcome(match_result.then)
            dispatch = build_dispatch(rule, fact, outcome, dashboard_url, settings, rule_values)

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
