# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The default alerting definitions a new environment starts with - the `alerting`
# vocabulary the builder's completion menus speak and one ruleset per connection
# type the sweep matches facts through. Everything is seeded idempotently, each
# definition by its own name: a store that already holds one of them, published
# or not, keeps what it has, so nothing a person edited or archived ever comes
# back on its own, and an environment created before a type existed gains
# only the missing rulesets.

from __future__ import annotations

# stdlib
from logging import getLogger

# Zato
from zato.common.alerting.seed.rules_common import channels_rules, common_rules, scheduler_rules
from zato.common.alerting.seed.rules_connections import email_rules, file_transfer_rules, llm_rules, mcp_rules, \
    microsoft_rules, odoo_rules, rest_rules, sql_rules
from zato.common.api import Alerting
from zato.common.audit_log.api import AuditSource
from zato.common.rule_engine.document_checks import validate_definition_document
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Vocabulary, Documents_Key, \
    System_Actor
from zato.common.rule_engine.vocabulary import TermType

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
    from zato.common.typing_ import anydict
    anydict = anydict
    RuleDefinitionRecord = RuleDefinitionRecord
    RuleSQLBackend = RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The comment the first version of each seeded definition carries.
_seed_comment = 'The alerting definitions a new environment starts with'

# A term that is neither deprecated nor otherwise marked carries no status.
_no_status = ''

# The audit sources a rule may narrow itself to - the value list behind `alert.source`.
_alert_sources = [
    AuditSource.PubSub,
    AuditSource.REST_Channel,
    AuditSource.SOAP_Channel,
    AuditSource.REST_Outgoing,
    AuditSource.SOAP_Outgoing,
    AuditSource.REST_Outgoing_Health,
    AuditSource.SOAP_Outgoing_Health,
    AuditSource.Email_IMAP,
    AuditSource.Email_SMTP,
    AuditSource.File_Outgoing,
    AuditSource.SQL_Outgoing,
    AuditSource.AS2,
    AuditSource.AS4,
    AuditSource.X12,
    AuditSource.MCP,
    AuditSource.MLLP_Channel,
    AuditSource.MLLP_Outgoing,
    AuditSource.FHIR,
    AuditSource.Config,
    AuditSource.Scheduler,
    AuditSource.LLM,
    AuditSource.Odoo,
    AuditSource.Microsoft_Cloud,
    AuditSource.Certificate,
    AuditSource.Microsoft_Health,
    AuditSource.Canary,
]

# The actions an outcome may name - the value list behind `outcome.action`.
_outcome_actions = [
    'diagnose',
    'email',
    'slack',
    'teams',
    'webhook',
    'invoke-service',
    'publish-to-topic',
]

# The severities an outcome may carry - the value list behind `outcome.severity`.
_outcome_severities = [
    'info',
    'warning',
    'critical',
]

# The health states a remote service may report about itself - the value list
# behind `alert.health_state`. The probe normalizes whatever the provider says
# into these two, so the rules never chase provider-specific spellings.
_health_states = [
    'degraded',
    'interruption',
]

# The canary rule ships inactive because the canary writes to remote systems -
# activating the rule together with the canary job is the documented opt-in.
_inactive_rule_full_names = [
    'alerts_file_transfer_Canary_Failing',
]

# ################################################################################################################################
# ################################################################################################################################

# The seed table - every default ruleset by name, seeded in one loop with the same
# idempotent per-name existence check. An environment that already customized one
# of them gains only the missing ones. The single `alerts` ruleset from before the
# per-type split is not here on purpose - environments that hold it keep it, and
# the sweep's prefix matching runs it alongside these.
default_rulesets = [
    ('alerts_common',        common_rules),
    ('alerts_channels',      channels_rules),
    ('alerts_rest',          rest_rules),
    ('alerts_sql',           sql_rules),
    ('alerts_llm',           llm_rules),
    ('alerts_mcp',           mcp_rules),
    ('alerts_microsoft',     microsoft_rules),
    ('alerts_email',         email_rules),
    ('alerts_odoo',          odoo_rules),
    ('alerts_file_transfer', file_transfer_rules),
    ('alerts_scheduler',     scheduler_rules),
]

# ################################################################################################################################
# ################################################################################################################################

def _term(name:'str', type_:'str', phrase:'str', *, values:'list[str] | None'=None) -> 'anydict':
    """ One vocabulary attribute - the name rules use, the type that decides which comparators fit
    and the phrase every screen speaks it with. A choice term also carries its legal values.
    """
    out:'anydict' = {'name': name, 'type': type_, 'phrase': phrase, 'status': _no_status}

    if values is not None:
        out['values'] = values

    return out

# ################################################################################################################################

def alerting_vocabulary() -> 'anydict':
    """ The terms the alert rules are written in - what the collectors measure about an object
    and what a matching rule decides about it.
    """
    alert_terms = [
        _term('source',                 TermType.Choice, 'the kind of object the measures are about', values=_alert_sources),
        _term('object_name',            TermType.Text,   'the name of the object the measures are about'),
        _term('error_rate',             TermType.Number, 'the share of error outcomes within the window'),
        _term('error_count',            TermType.Number, 'how many error outcomes the window holds'),
        _term('total_count',            TermType.Number, 'how many events the window holds in total'),
        _term('window_seconds',         TermType.Number, 'how many seconds the error measures cover'),
        _term('outstanding',            TermType.Number, 'how many messages still wait for their follow-up'),
        _term('oldest_waiting_seconds', TermType.Number, 'how long the oldest waiting message has been waiting'),
        _term('silent_seconds',         TermType.Number, 'how long the feed has been silent'),
        _term('consecutive_failures',   TermType.Number, 'how many of the newest outcomes are errors, without a break'),
        _term('avg_duration_ms',        TermType.Number, 'the average duration of completed calls within the window'),
        _term('auth_failure_count',     TermType.Number, 'how many authentication failures the window holds'),
        _term('cert_days_left',         TermType.Number, 'how many days the TLS certificate has left, zero when unmeasured'),
        _term('health_state',           TermType.Choice, 'the health state the remote service reports about itself',
            values=_health_states),
        _term('canary_failed',          TermType.Number, 'whether the newest canary check failed'),
        _term('overdue_ratio',          TermType.Number, 'time since the newest run as a multiple of the job interval'),
        _term('start_delay_ms',         TermType.Number, 'the worst delay between planned and actual fire time in the window'),
    ]

    outcome_terms = [
        _term('action',               TermType.Choice, 'what happens when the rule fires', values=_outcome_actions),
        _term('severity',             TermType.Choice, 'how severe the alert is', values=_outcome_severities),
        _term('llm_connection',       TermType.Text,   'the LLM connection an alert diagnosis goes through'),
        _term('dashboard_url',        TermType.Text,   'the dashboard address notification links point to'),
        _term('addresses',            TermType.Text,   'the comma-separated addresses an email alert goes to'),
        _term('service',              TermType.Text,   'the service an invoke-service action calls'),
        _term('topic',                TermType.Text,   'the topic a publish-to-topic action publishes to'),
        _term('webhook_url',          TermType.Text,   'the webhook a Slack or Teams alert posts to'),
        _term('link',                 TermType.Text,   'the dashboard path the alert message links to'),
        _term('dedup_window_seconds', TermType.Number, 'how long repeated matches increment the alert instead of raising anew'),
    ]

    entities = [
        {'name': 'alert', 'attributes': alert_terms},
        {'name': 'outcome', 'attributes': outcome_terms},
    ]

    out = {'name': Alerting.Vocabulary_Name, 'entities': entities}
    return out

# ################################################################################################################################

def build_ruleset_document(ruleset_name:'str', zrules_contents:'str') -> 'anydict':
    """ One default ruleset as the canonical documents the store keeps,
    parsed from the same text form the builder produces.
    """
    documents, errors = parse_data_details(zrules_contents, ruleset_name)

    if errors:
        raise Exception(f'The default alert rules of `{ruleset_name}` do not parse -> {errors}')

    # The rules that ship turned off are marked so before they ever reach the store
    for full_name in _inactive_rule_full_names:
        if full_name in documents:
            documents[full_name]['is_active'] = False

    out = {Documents_Key: documents}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _exists(backend:'RuleSQLBackend', name:'str', object_type:'str') -> 'bool':
    """ Whether the store already holds one seeded definition, under the name and the kind
    it is created with. Archived ones count too - what was put aside on purpose stays that way.
    """
    candidates = backend.definitions.list(object_type=object_type, include_inactive=True, search_text=name)

    for candidate in candidates:
        if candidate.name == name:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def _create_definition(
    backend:'RuleSQLBackend',
    *,
    name:'str',
    object_type:'str',
    document:'anydict',
    ) -> 'RuleDefinitionRecord':
    """ Stores one seeded definition together with its first version, after the same validation the screens run.
    """
    errors = validate_definition_document(object_type, document)

    if errors:
        raise Exception(f'The default alerting {object_type} does not validate -> {errors}')

    out = backend.definitions.create(
        name=name,
        object_type=object_type,
        document=document,
        author=System_Actor,
        comment=_seed_comment,
    )

    logger.info('Created the default alerting %s `%s` (id=%s)', object_type, name, out.id)
    return out

# ################################################################################################################################

def _seed_vocabulary(backend:'RuleSQLBackend') -> 'bool':
    """ The vocabulary comes first, because the rulesets speak its terms.
    """
    if _exists(backend, Alerting.Vocabulary_Name, Definition_Type_Vocabulary):
        return False

    vocabulary = _create_definition(
        backend,
        name=Alerting.Vocabulary_Name,
        object_type=Definition_Type_Vocabulary,
        document=alerting_vocabulary(),
    )
    _ = backend.versions.publish(definition_id=vocabulary.id, version=vocabulary.current_version, actor=System_Actor)

    return True

# ################################################################################################################################

def _seed_ruleset(backend:'RuleSQLBackend', ruleset_name:'str', zrules_contents:'str') -> 'bool':
    """ One default ruleset goes live in the same call, so the very first sweep already has it.
    """
    if _exists(backend, ruleset_name, Definition_Type_Ruleset):
        return False

    document = build_ruleset_document(ruleset_name, zrules_contents)
    ruleset = _create_definition(
        backend,
        name=ruleset_name,
        object_type=Definition_Type_Ruleset,
        document=document,
    )

    documents = document[Documents_Key]
    _ = backend.references.rebuild(definition_id=ruleset.id, documents=documents)
    _ = backend.versions.publish(definition_id=ruleset.id, version=ruleset.current_version, actor=System_Actor)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_alerting_definitions(backend:'RuleSQLBackend') -> 'None':
    """ Gives an environment the alerting vocabulary and the default alert rulesets.

    Each one is looked up by its own name and kind, so a store that already holds
    some of them gains only what is missing, and anything a person edited themselves
    is never touched.
    """
    created_any = _seed_vocabulary(backend)

    for ruleset_name, zrules_contents in default_rulesets:
        created_ruleset = _seed_ruleset(backend, ruleset_name, zrules_contents)
        created_any = created_any or created_ruleset

    if created_any:
        logger.info('Default alerting definitions seeded')

# ################################################################################################################################
# ################################################################################################################################
