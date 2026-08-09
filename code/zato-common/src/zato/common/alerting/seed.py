# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The default alerting definitions a new environment starts with - the `alerting`
# vocabulary the builder's completion menus speak and the `alerts` ruleset the sweep
# matches facts through. Both are seeded idempotently: a store that already holds one
# of them, published or not, keeps what it has, so nothing a person edited or archived
# ever comes back on its own.

from __future__ import annotations

# stdlib
from logging import getLogger

# Zato
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
]

# The actions an outcome may name - the value list behind `outcome.action`.
_outcome_actions = [
    'incident',
    'email',
    'slack',
    'teams',
    'invoke-service',
    'publish-to-topic',
]

# The severities an outcome may carry - the value list behind `outcome.severity`.
_outcome_severities = [
    'info',
    'warning',
    'critical',
]

# ################################################################################################################################
# ################################################################################################################################

# The default alert rules - one per kind of trouble the collectors can measure, each
# covering the sources that produce that measure. The REST outgoing one dispatches
# an incident diagnosis, the rest raise email alerts a devops person tunes or turns off.
default_alerts_zrules_contents = """
# ################################################################################################################################

rule
    REST_Outgoing_Error_Rate
docs
    A REST outgoing connection whose error share reached a quarter of its recent traffic is diagnosed as an incident.
when
    alert.source is 'rest-outgoing' and
    alert.error_rate is at least 0.25
then
    outcome.action = 'incident'

# ################################################################################################################################

rule
    Channel_Error_Rate
docs
    An inbound channel whose error share reached a quarter of its recent traffic raises an email alert.
when
    alert.source in ['rest-channel', 'soap-channel', 'mllp-channel'] and
    alert.error_rate is at least 0.25
then
    outcome.action = 'email'

# ################################################################################################################################

rule
    Outgoing_Error_Rate
docs
    A non-REST outgoing connection whose error share reached a quarter of its recent traffic raises an email alert.
when
    alert.source in ['soap-outgoing', 'sql-outgoing', 'email-smtp', 'file-outgoing', 'mllp-outgoing'] and
    alert.error_rate is at least 0.25
then
    outcome.action = 'email'

# ################################################################################################################################

rule
    Scheduler_Error_Rate
docs
    Scheduled jobs whose error share reached a quarter of their recent runs raise an email alert.
when
    alert.source is 'scheduler' and
    alert.error_rate is at least 0.25
then
    outcome.action = 'email'

# ################################################################################################################################

rule
    Outstanding_Backlog
docs
    An object with a hundred or more messages still waiting for their follow-up raises an email alert.
when
    alert.outstanding is at least 100
then
    outcome.action = 'email'

# ################################################################################################################################

rule
    Feed_Silent
docs
    A feed that has been silent for two hours or more raises an email alert.
when
    alert.silent_seconds is at least 7200
then
    outcome.action = 'email'

# ################################################################################################################################
""".strip()

# ################################################################################################################################
# ################################################################################################################################

def _term(name:'str', type_:'str', phrase:'str', *, values:'list[str] | None'=None) -> 'anydict':
    """ One vocabulary attribute - the name rules use, the type that decides which comparators fit
    and the phrase every screen speaks it with. A choice term also carries its legal values.
    """
    out = {'name': name, 'type': type_, 'phrase': phrase, 'status': _no_status}

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
    ]

    outcome_terms = [
        _term('action',               TermType.Choice, 'what happens when the rule fires', values=_outcome_actions),
        _term('severity',             TermType.Choice, 'how severe the alert is', values=_outcome_severities),
        _term('llm_conn',             TermType.Text,   'the LLM connection an incident diagnosis goes through'),
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

def alerts_ruleset() -> 'anydict':
    """ The default alert rules as the canonical documents the store keeps,
    parsed from the same text form the builder produces.
    """
    documents, errors = parse_data_details(default_alerts_zrules_contents, Alerting.Ruleset_Name)

    if errors:
        raise Exception(f'The default alert rules do not parse -> {errors}')

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
    """ The vocabulary comes first, because the ruleset speaks its terms.
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

def _seed_ruleset(backend:'RuleSQLBackend') -> 'bool':
    """ The default rules go live in the same call, so the very first sweep already has them.
    """
    if _exists(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset):
        return False

    document = alerts_ruleset()
    ruleset = _create_definition(
        backend,
        name=Alerting.Ruleset_Name,
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
    """ Gives an environment the alerting vocabulary and the default alert rules.

    Each one is looked up by its own name and kind, so a store that already holds
    some of them gains only what is missing, and anything a person edited themselves
    is never touched.
    """
    created_vocabulary = _seed_vocabulary(backend)
    created_ruleset = _seed_ruleset(backend)

    if created_vocabulary or created_ruleset:
        logger.info('Default alerting definitions seeded')

# ################################################################################################################################
# ################################################################################################################################
