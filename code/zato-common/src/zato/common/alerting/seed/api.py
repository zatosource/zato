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
from zato.common.rule_engine.sql.document import deserialize_document
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

# The comment an upgrade version carries when a newer release ships definitions
# an existing environment does not hold yet.
_upgrade_comment = 'New default alerting definitions gained on upgrade'

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
        _term('seconds_since_last_arrival', TermType.Number, 'how long ago a schedule last received a file'),
        _term('arrival_overdue_ratio',  TermType.Number, 'time since the newest file as a multiple of the schedule arrival window'),
    ]

    outcome_terms = [
        _term('action',               TermType.Choice, 'what happens when the rule fires', values=_outcome_actions),
        _term('severity',             TermType.Choice, 'how severe the alert is', values=_outcome_severities),
        _term('llm_connection',       TermType.Text,   'the LLM connection an alert diagnosis goes through'),
        _term('dashboard_url',        TermType.Text,   'the dashboard address notification links point to'),
        _term('addresses',            TermType.Text,   'the comma-separated addresses an email alert goes to'),
        _term('slack_channel',        TermType.Text,   'the channel a Slack alert posts to'),
        _term('teams_to',             TermType.Text,   'the team and channel a Teams alert goes to'),
        _term('service',              TermType.Text,   'the service an invoke-service action calls'),
        _term('topic',                TermType.Text,   'the topic a publish-to-topic action publishes to'),
        _term('webhook_url',          TermType.Text,   'the URL a webhook alert posts to'),
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

def _find_active(backend:'RuleSQLBackend', name:'str', object_type:'str') -> 'RuleDefinitionRecord | None':
    """ The one active definition of the given name and kind - what an upgrade works on.
    An archived one stays out on purpose, because what was put aside stays that way.
    """
    records = backend.definitions.find_by_name(name=name, object_type=object_type)

    if records:
        out = records[0]
    else:
        out = None

    return out

# ################################################################################################################################

def _historical_documents(backend:'RuleSQLBackend', definition:'RuleDefinitionRecord') -> 'list[anydict]':
    """ The document of every version one definition ever had, oldest first. This is what tells
    a rule a person deleted apart from a rule a newer release ships - the deleted one appeared
    in some earlier version, the new one never did. Versions are numbered consecutively
    from one, so walking them needs no listing API.
    """

    # Our response to produce
    out:'list[anydict]' = []

    for version_number in range(1, definition.current_version + 1):
        version = backend.versions.get(definition.id, version_number)
        out.append(deserialize_document(version.document))

    return out

# ################################################################################################################################

def _store_upgrade(backend:'RuleSQLBackend', definition:'RuleDefinitionRecord', document:'anydict') -> 'None':
    """ Stores one upgraded document as a new published version of an existing definition,
    the same path a person's own edit takes.
    """
    version = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=definition.current_version,
        document=document,
        author=System_Actor,
        comment=_upgrade_comment,
    )

    # A ruleset's reference index follows its rules
    if definition.object_type == Definition_Type_Ruleset:
        _ = backend.references.rebuild(definition_id=definition.id, documents=document[Documents_Key])

    _ = backend.versions.publish(definition_id=definition.id, version=version.version, actor=System_Actor)

# ################################################################################################################################

def _upgrade_vocabulary(backend:'RuleSQLBackend') -> 'bool':
    """ Gives an existing vocabulary the terms a newer release ships. A term is added only
    when no version of the vocabulary ever held it - a term missing now that some earlier
    version did hold was removed by a person and stays removed, and anything
    a person edited themselves is never touched.
    """
    definition = _find_active(backend, Alerting.Vocabulary_Name, Definition_Type_Vocabulary)

    # No vocabulary means the seeding itself is what runs, not an upgrade
    if definition is None:
        return False

    document = deserialize_document(definition.document)
    shipped = alerting_vocabulary()

    # The stored entities by name, so the shipped ones can be matched up
    stored_entities = {}

    for entity in document['entities']:
        stored_entities[entity['name']] = entity

    # What the current document is missing, as (entity name, attribute) pairs
    missing:'list[tuple[str, anydict]]' = []

    for shipped_entity in shipped['entities']:

        # A whole entity the store never saw is missing with all its attributes ..
        if shipped_entity['name'] not in stored_entities:
            for attribute in shipped_entity['attributes']:
                missing.append((shipped_entity['name'], attribute))
            continue

        # .. and an existing one may be missing some of the shipped attributes.
        stored_entity = stored_entities[shipped_entity['name']]

        stored_names = set()

        for attribute in stored_entity['attributes']:
            stored_names.add(attribute['name'])

        for attribute in shipped_entity['attributes']:
            if attribute['name'] not in stored_names:
                missing.append((shipped_entity['name'], attribute))

    # Nothing missing means nothing to store, and the history stays unread
    if not missing:
        return False

    # Every (entity, attribute) pair any version ever held - what was there
    # once and is gone now was removed by a person on purpose.
    ever_present = set()

    for historical in _historical_documents(backend, definition):
        for entity in historical['entities']:
            for attribute in entity['attributes']:
                ever_present.add((entity['name'], attribute['name']))

    added_any = False

    for entity_name, attribute in missing:

        # A term some earlier version held was removed on purpose and stays removed
        if (entity_name, attribute['name']) in ever_present:
            continue

        # A whole new entity is grown the moment its first attribute arrives
        if entity_name not in stored_entities:
            new_entity = {'name': entity_name, 'attributes': []}
            document['entities'].append(new_entity)
            stored_entities[entity_name] = new_entity

        stored_entities[entity_name]['attributes'].append(attribute)
        added_any = True

    # Everything missing was removed by a person, so there is nothing to store
    if not added_any:
        return False

    _store_upgrade(backend, definition, document)

    logger.info('Upgraded the alerting vocabulary `%s` with new terms', Alerting.Vocabulary_Name)
    return True

# ################################################################################################################################

def _upgrade_ruleset(backend:'RuleSQLBackend', ruleset_name:'str', zrules_contents:'str') -> 'bool':
    """ Gives an existing default ruleset the rules a newer release ships. A rule is added only
    when no version of the ruleset ever held it - a rule missing now that some earlier version
    did hold was deleted by a person and stays deleted, and anything a person edited
    themselves is never touched.
    """
    definition = _find_active(backend, ruleset_name, Definition_Type_Ruleset)

    # No such ruleset means the seeding itself is what runs, not an upgrade
    if definition is None:
        return False

    document = deserialize_document(definition.document)
    documents = document[Documents_Key]

    shipped = build_ruleset_document(ruleset_name, zrules_contents)

    # What the current document is missing, by each rule's full name
    missing = []

    for full_name in shipped[Documents_Key]:
        if full_name not in documents:
            missing.append(full_name)

    # Nothing missing means nothing to store, and the history stays unread
    if not missing:
        return False

    # Every rule name any version ever held - what was there once
    # and is gone now was deleted by a person on purpose.
    ever_present = set()

    for historical in _historical_documents(backend, definition):
        ever_present.update(historical[Documents_Key])

    added_any = False

    for full_name in missing:

        # A rule some earlier version held was deleted on purpose and stays deleted
        if full_name in ever_present:
            continue

        documents[full_name] = shipped[Documents_Key][full_name]
        added_any = True

    # Everything missing was deleted by a person, so there is nothing to store
    if not added_any:
        return False

    _store_upgrade(backend, definition, document)

    logger.info('Upgraded the default alerting ruleset `%s` with new rules', ruleset_name)
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

    # A vocabulary that already existed may still be missing the terms
    # a newer release ships - the upgrade adds only what is absent by name.
    if not created_any:
        _ = _upgrade_vocabulary(backend)

    for ruleset_name, zrules_contents in default_rulesets:
        created_ruleset = _seed_ruleset(backend, ruleset_name, zrules_contents)
        created_any = created_any or created_ruleset

        # An already-seeded ruleset gains the rules a newer release ships,
        # each one looked up by its own full name.
        if not created_ruleset:
            _ = _upgrade_ruleset(backend, ruleset_name, zrules_contents)

    if created_any:
        logger.info('Default alerting definitions seeded')

# ################################################################################################################################
# ################################################################################################################################
