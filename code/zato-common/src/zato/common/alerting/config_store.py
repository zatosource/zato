# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One shared write path from screen-shaped alert config values into the live rule
# documents - the web admin's config screen and the CLI's enmasse importer both go
# through here, so a value saved on the screen and a value imported from YAML take
# the same steps: rewrite through config_map, store a new version, publish it.

from __future__ import annotations

# Zato
from zato.common.alerting import config_map
from zato.common.rule_engine import webapi
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
    from zato.common.typing_ import stranydict
    RuleDefinitionRecord = RuleDefinitionRecord
    RuleSQLBackend = RuleSQLBackend
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class NoSuchRulesetError(Exception):
    """ Raised when a type's ruleset does not exist in the store at all.
    """

# ################################################################################################################################
# ################################################################################################################################

def get_type_definition(backend:'RuleSQLBackend', type_name:'str') -> 'RuleDefinitionRecord':
    """ One type's live ruleset definition, or an error when the store does not hold it.
    """
    ruleset_name = config_map.type_to_ruleset[type_name]
    matches = backend.definitions.find_by_name(name=ruleset_name, object_type=Definition_Type_Ruleset)

    if not matches:
        raise NoSuchRulesetError(f'No such ruleset -> {ruleset_name}')

    out = matches[0]
    return out

# ################################################################################################################################

def apply_type_config(
    backend:'RuleSQLBackend',
    type_name:'str',
    *,
    actor:'str',
    values:'stranydict | None'=None,
    is_active:'bool | None'=None,
    comment:'str'='',
    ) -> 'bool':
    """ Writes screen-shaped values and/or the type's active state into its live rule
    documents, storing and publishing a new version only when something actually
    changed - saving what is already there creates nothing. Returns whether it changed.
    """
    definition = get_type_definition(backend, type_name)

    document = deserialize_document(definition.document)
    documents = document[Documents_Key]

    # Our response to produce
    changed = False

    # The type-level flag goes first and only moves when the type's overall state
    # actually differs - a field toggle travelling in the same save then refines it
    # rather than being overwritten, which is what keeps a YAML entry that says
    # is_active with a toggle turned off both correct and idempotent.
    if is_active is not None:
        if config_map.is_type_active(documents) != is_active:
            active_changed = config_map.set_type_active(documents, is_active)
            changed = changed or active_changed

    if values is not None:
        values_changed = config_map.write_type_values(type_name, documents, values)
        changed = changed or values_changed

    # Nothing moved, so no new version appears - what keeps repeated saves idempotent
    if not changed:
        return False

    if not comment:
        comment = f'Updated alert config for type {type_name}'

    body = {
        'definition_id': definition.id,
        'expected_current_version': definition.current_version,
        'document': {Documents_Key: documents},
        'comment': comment,
    }
    result, _ = webapi.save_document(backend, body, actor)

    # The change goes live in the same call, so the next sweep already runs with it
    _ = backend.versions.publish(definition_id=definition.id, version=result['version'], actor=actor)

    return True

# ################################################################################################################################
# ################################################################################################################################
