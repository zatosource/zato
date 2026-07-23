# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.api import RulesManager
    from zato.common.rule_engine.sql import RuleSQLBackend, RuleVersionRecord
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class LoadedVersion(NamedTuple):
    """ Which stored snapshot a manager now runs and the full names of its rules, in rule order.
    """
    rule_names: 'strlist'
    version: 'int'

# ################################################################################################################################
# ################################################################################################################################

def documents_from_version(record:'RuleVersionRecord') -> 'anydict':
    """ Returns the canonical rule documents one stored version snapshot carries.
    """
    payload = deserialize_document(record.document)

    # A runnable ruleset snapshot always keeps its rules under the documents key - anything else cannot be loaded.
    if Documents_Key not in payload:
        message = f'Version {record.version} of definition {record.definition_id} has no `{Documents_Key}` key'
        raise Exception(message)

    out = payload[Documents_Key]

    # An empty snapshot cannot decide anything, which is an authoring error, never a silent no-op.
    if not out:
        message = f'Version {record.version} of definition {record.definition_id} has no rule documents'
        raise Exception(message)

    return out

# ################################################################################################################################

def load_live_ruleset(manager:'RulesManager', backend:'RuleSQLBackend', definition_id:'int') -> 'LoadedVersion':
    """ Loads a definition's live version from the SQL store, replacing the whole ruleset in the manager.
    """
    # Resolve the one live snapshot and its rule documents ..
    record = backend.versions.get_live(definition_id)
    documents = documents_from_version(record)

    # .. every document of one load belongs to the same ruleset ..
    first = next(iter(documents.values()))
    ruleset_name = first['ruleset_name']

    # .. and swap the complete ruleset in place, without recreating the manager.
    rule_names = manager.load_parsed_rules(documents, ruleset_name)

    out = LoadedVersion(rule_names, record.version)
    return out

# ################################################################################################################################

def publish_and_reload(
    manager:'RulesManager',
    backend:'RuleSQLBackend',
    *,
    definition_id:'int',
    version:'int',
    actor:'str',
    ) -> 'LoadedVersion':
    """ Publishes one stored version and hot-reloads it into the manager in the same call.
    """
    # Make the requested snapshot live ..
    _ = backend.versions.publish(definition_id=definition_id, version=version, actor=actor)

    # .. and run it without a restart.
    out = load_live_ruleset(manager, backend, definition_id)
    return out

# ################################################################################################################################
# ################################################################################################################################
