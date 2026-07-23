# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.rules.api import RulesManager
from zato.common.rules.loading import documents_from_version, load_live_ruleset, publish_and_reload
from zato.common.rules.parser import parse_data_details
from zato.common.rules.sql import RecordNotFoundError, RuleDefinitionRecord, RuleSQLBackend
from zato.common.rules.sql.constants import Definition_Type_Ruleset, Documents_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_author = 'anna.k'

# The first version approves excellent scores only, the second one lowers the bar.
_rules_v1 = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
when
    credit_score is at least 700
then
    rate = 2.9
    approved = true
"""

_rules_v2 = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
when
    credit_score is at least 640
then
    rate = 3.4
    approved = true
"""

# ################################################################################################################################
# ################################################################################################################################

def _documents(rules_text:'str') -> 'anydict':
    """ Parses rules text into canonical documents keyed by full name.
    """
    documents, errors = parse_data_details(rules_text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################

def _create_ruleset(backend:'RuleSQLBackend', rules_text:'str') -> 'RuleDefinitionRecord':
    """ Stores one ruleset definition whose document carries canonical rule documents.
    """
    document = {Documents_Key: _documents(rules_text)}

    out = backend.definitions.create(
        name='Loans',
        object_type=Definition_Type_Ruleset,
        document=document,
        author=_author,
        comment='Create the loans ruleset',
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_load_live_ruleset_runs_stored_rules(backend:'RuleSQLBackend') -> 'None':
    """ A published version loads from SQL into a manager that then decides with it.
    """
    # Store and publish the first version ..
    definition = _create_ruleset(backend, _rules_v1)
    _ = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)

    # .. load the live version into a fresh manager ..
    manager = RulesManager()
    loaded = load_live_ruleset(manager, backend, definition.id)

    assert loaded.version == 1
    assert loaded.rule_names == ['loans_Preferential_rate']

    # .. and the manager decides with exactly the stored rules.
    rule = manager['loans_Preferential_rate']
    result = rule.match({'credit_score': 720})

    assert result
    assert result.then['rate'] == 2.9

# ################################################################################################################################

def test_no_live_version_is_loud(backend:'RuleSQLBackend') -> 'None':
    """ Loading a definition that was never published fails loudly.
    """
    definition = _create_ruleset(backend, _rules_v1)
    manager = RulesManager()

    with pytest.raises(RecordNotFoundError):
        _ = load_live_ruleset(manager, backend, definition.id)

# ################################################################################################################################

def test_snapshot_without_documents_is_loud(backend:'RuleSQLBackend') -> 'None':
    """ A stored snapshot without canonical documents cannot be loaded silently.
    """
    definition = backend.definitions.create(
        name='Not runnable',
        object_type=Definition_Type_Ruleset,
        document={'rules': []},
        author=_author,
        comment='Create a snapshot without documents',
    )
    version = backend.versions.get(definition.id, 1)

    with pytest.raises(Exception, match=Documents_Key):
        _ = documents_from_version(version)

# ################################################################################################################################

def test_publish_and_reload_swaps_rules_in_place(backend:'RuleSQLBackend') -> 'None':
    """ Publishing a new version hot-reloads the same manager without recreating it.
    """
    # Publish and load the first version ..
    definition = _create_ruleset(backend, _rules_v1)
    _ = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)

    manager = RulesManager()
    _ = load_live_ruleset(manager, backend, definition.id)

    # .. a score of 660 is below the first version's bar ..
    rule = manager['loans_Preferential_rate']
    assert not rule.match({'credit_score': 660})

    # .. store the second version and make it live in one call ..
    _ = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=1,
        document={Documents_Key: _documents(_rules_v2)},
        author=_author,
        comment='Lower the bar for the preferential rate',
    )
    loaded = publish_and_reload(manager, backend, definition_id=definition.id, version=2, actor=_author)

    assert loaded.version == 2

    # .. and the same manager now decides with the new version.
    rule = manager['loans_Preferential_rate']
    result = rule.match({'credit_score': 660})

    assert result
    assert result.then['rate'] == 3.4

# ################################################################################################################################

def test_reload_drops_rules_the_new_version_no_longer_has(backend:'RuleSQLBackend') -> 'None':
    """ A rule deleted between versions stops existing in the manager after a reload.
    """
    # The first load carries two rules ..
    two_rules = _rules_v1 + """
rule
    Large_amount_review
docs
    Large amounts need a manual look.
when
    amount is more than 100000
then
    needs_review = true
"""
    definition = _create_ruleset(backend, two_rules)
    _ = backend.versions.publish(definition_id=definition.id, version=1, actor=_author)

    manager = RulesManager()
    loaded = load_live_ruleset(manager, backend, definition.id)
    assert len(loaded.rule_names) == 2

    # .. the second version deletes one of them ..
    _ = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=1,
        document={Documents_Key: _documents(_rules_v1)},
        author=_author,
        comment='Delete the review rule',
    )
    loaded = publish_and_reload(manager, backend, definition_id=definition.id, version=2, actor=_author)
    assert loaded.rule_names == ['loans_Preferential_rate']

    # .. and the deleted rule is gone from the manager, not just from the list.
    with pytest.raises(AttributeError):
        _ = manager['loans_Large_amount_review']

# ################################################################################################################################
# ################################################################################################################################
