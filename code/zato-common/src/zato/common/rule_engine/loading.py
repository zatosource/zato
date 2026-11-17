# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.rule_engine.api import RulesManager
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleVersionRecord
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class LoadedRules(NamedTuple):
    """ A manager with one ruleset loaded and the full names of its rules, in rule order.
    """
    manager: 'RulesManager'
    rule_names: 'strlist'

# ################################################################################################################################
# ################################################################################################################################

def load_documents(documents:'anydict') -> 'LoadedRules':
    """ Loads canonical rule documents into a fresh manager, ready to evaluate inputs.
    """
    if not documents:
        raise Exception('There are no documents to load')

    # Every document of one load belongs to the same ruleset.
    first = next(iter(documents.values()))
    ruleset_name = first['ruleset_name']

    manager = RulesManager()
    rule_names = manager.load_parsed_rules(documents, ruleset_name)

    out = LoadedRules(manager, rule_names)
    return out

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
# ################################################################################################################################
