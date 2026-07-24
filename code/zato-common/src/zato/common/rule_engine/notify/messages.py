# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# Zato
from zato.common.rule_engine.diff import diff_documents
from zato.common.rule_engine.notify.documents import documents_of_version
from zato.common.rule_engine.sql.constants import Event_Type_Advisory_Run, Event_Type_Decisions_Spiked, \
    Event_Type_Version_Published, Event_Type_Version_Restored

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleEventRecord, RuleSQLBackend
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# Where the dashboard runs - when set, every message ends with a deep link into the ruleset.
Env_Dashboard_Base_URL = 'Zato_Rule_Engine_Dashboard_Base_URL'

# The dashboard's path to one ruleset, appended to the base URL above.
Ruleset_Path = '/rules/rulesets/{definition_id}/'

# How many changed rule names a change summary spells out before switching to a count.
Max_Named_Rules = 3

# ################################################################################################################################
# ################################################################################################################################

def _named_rules(names:'strlist') -> 'str':
    """ Spells out up to a few rule names, folding the rest into a count.
    """
    named = names[:Max_Named_Rules]
    remaining = len(names) - len(named)
    out = ', '.join(named)

    if remaining:
        out = f'{out} and {remaining} more'

    return out

# ################################################################################################################################

def change_summary(backend:'RuleSQLBackend', definition_id:'int', version:'int') -> 'str':
    """ Returns a one-line summary of what changed between a version and its predecessor,
    or an empty string when there is nothing to compare.
    """
    # The first version has no predecessor to compare against ..
    if version < 2:
        return ''

    # .. both snapshots have to carry rule documents ..
    old_documents = documents_of_version(backend, definition_id, version - 1)
    new_documents = documents_of_version(backend, definition_id, version)

    if old_documents is None:
        return ''

    if new_documents is None:
        return ''

    # .. diff them structurally ..
    result = diff_documents(old_documents, new_documents)
    parts = []

    # .. and describe each kind of change that actually happened ..
    added_count = len(result['added'])
    if added_count:
        suffix = 'rule' if added_count == 1 else 'rules'
        parts.append(f'{added_count} {suffix} added')

    updated_count = len(result['updated'])
    if updated_count:
        updated_names = []
        for entry in result['updated']:
            updated_names.append(entry['rule'])

        named = _named_rules(updated_names)
        suffix = 'rule' if updated_count == 1 else 'rules'
        parts.append(f'{updated_count} {suffix} updated ({named})')

    deleted_count = len(result['deleted'])
    if deleted_count:
        suffix = 'rule' if deleted_count == 1 else 'rules'
        parts.append(f'{deleted_count} {suffix} deleted')

    renamed_count = len(result['renamed'])
    if renamed_count:
        suffix = 'rule' if renamed_count == 1 else 'rules'
        parts.append(f'{renamed_count} {suffix} renamed')

    # .. an all-unchanged diff produces no summary at all.
    if not parts:
        return ''

    joined = ', '.join(parts)

    out = f' - {joined}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def _build_published(
    backend:'RuleSQLBackend',
    event:'RuleEventRecord',
    definition:'RuleDefinitionRecord',
    payload:'anydict',
    ) -> 'str':
    """ The message for a version going live.
    """
    version = payload['published_version']
    summary = change_summary(backend, definition.id, version)

    out = f"'{definition.name}' version {version} is live, published by {event.actor}.{summary}"
    return out

# ################################################################################################################################

def _build_restored(
    backend:'RuleSQLBackend',
    event:'RuleEventRecord',
    definition:'RuleDefinitionRecord',
    payload:'anydict',
    ) -> 'str':
    """ The message for a rollback.
    """
    _ = backend
    source_version = payload['source_version']

    out = f"'{definition.name}' was rolled back to version {source_version} by {event.actor}, " + \
        f'now live as version {event.version}.'
    return out

# ################################################################################################################################

def _build_advisory(
    backend:'RuleSQLBackend',
    event:'RuleEventRecord',
    definition:'RuleDefinitionRecord',
    payload:'anydict',
    ) -> 'str':
    """ The message for failing advisory tests.
    """
    _ = backend
    failed = payload['failed']
    total = payload['total']
    suite_name = payload['test_set_name']

    out = f"{failed} of {total} scenarios fail against version {event.version} of '{definition.name}' " + \
        f"(suite '{suite_name}')."
    return out

# ################################################################################################################################

def _build_spiked(
    backend:'RuleSQLBackend',
    event:'RuleEventRecord',
    definition:'RuleDefinitionRecord',
    payload:'anydict',
    ) -> 'str':
    """ The message for a decision traffic spike.
    """
    _ = backend
    _ = event
    count = payload['count']
    typical = payload['typical']

    out = f"'{definition.name}' decided {count:,} times in the last hour against a typical {typical:,}."
    return out

# ################################################################################################################################
# ################################################################################################################################

_builders = {
    Event_Type_Version_Published: _build_published,
    Event_Type_Version_Restored:  _build_restored,
    Event_Type_Advisory_Run:      _build_advisory,
    Event_Type_Decisions_Spiked:  _build_spiked,
}

# ################################################################################################################################
# ################################################################################################################################

def build_message(backend:'RuleSQLBackend', event:'RuleEventRecord') -> 'str':
    """ Turns one feed event into the complete message one destination receives.
    """
    # Every notified event names its ruleset ..
    definition = backend.definitions.get(event.definition_id)

    # .. the payload column is nullable in the database, though notified events always write one ..
    if event.payload is None:
        payload = {}
    else:
        payload = json.loads(event.payload)

    # .. build the event-specific text ..
    builder = _builders[event.event_type]
    out = builder(backend, event, definition, payload)

    # .. and finish with a deep link when the dashboard's address is known.
    if base_url := os.environ.get(Env_Dashboard_Base_URL):
        base_url = base_url.rstrip('/')
        path = Ruleset_Path.format(definition_id=definition.id)
        out = f'{out} {base_url}{path}'

    return out

# ################################################################################################################################
# ################################################################################################################################
