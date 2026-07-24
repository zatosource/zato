# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.sql import CapturePolicy, DecisionWrite
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Test_Set, Documents_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime

    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend, RuleVersionRecord
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

Author = 'anna.k'

# Flat terms evaluate directly against flat input mappings - this text backs every notification test.
Rules_Text = """
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

# The same rule with a lower bar - version two in the publish and diff tests.
Rules_Text_Lower_Bar = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
when
    credit_score is at least 640
then
    rate = 2.9
    approved = true
"""

# ################################################################################################################################
# ################################################################################################################################

def parse_documents(text:'str', ruleset_name:'str'='loans') -> 'anydict':
    """ Parses rules text into canonical documents, loud on any parse error.
    """
    documents, errors = parse_data_details(text, ruleset_name)
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################

def create_ruleset(
    backend:'RuleSQLBackend',
    name:'str'='Loans',
    text:'str'=Rules_Text,
    ) -> 'RuleDefinitionRecord':
    """ Stores one canonical ruleset definition.
    """
    documents = parse_documents(text)

    out = backend.definitions.create(
        name=name,
        object_type=Definition_Type_Ruleset,
        document={Documents_Key: documents},
        author=Author,
        comment='Create the ruleset',
    )

    return out

# ################################################################################################################################

def add_version(
    backend:'RuleSQLBackend',
    definition:'RuleDefinitionRecord',
    text:'str',
    comment:'str'='Lower the bar',
    ) -> 'RuleVersionRecord':
    """ Stores a new version of one ruleset.
    """
    documents = parse_documents(text)

    out = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=definition.current_version,
        document={Documents_Key: documents},
        author=Author,
        comment=comment,
    )

    return out

# ################################################################################################################################

def create_suite(
    backend:'RuleSQLBackend',
    ruleset_id:'int',
    *,
    expected_rate:'float',
    name:'str'='Loan suite',
    ) -> 'RuleDefinitionRecord':
    """ Attaches one advisory suite to one ruleset - the expected rate decides whether its scenario passes.
    """
    suite_document = {
        'name': name,
        'scenarios': [
            {
                'name': 'High score gets the rate',
                'input': {'credit_score': 720},
                'expected': {'rate': expected_rate, 'approved': True},
            },
        ],
    }

    out = backend.definitions.create(
        name=name,
        object_type=Definition_Type_Test_Set,
        document=suite_document,
        author=Author,
        comment='Create the test suite',
        parent_id=ruleset_id,
    )

    return out

# ################################################################################################################################

def seed_decisions(
    backend:'RuleSQLBackend',
    ruleset_id:'int',
    *,
    occurred_at:'datetime',
    count:'int',
    decision_id_prefix:'str',
    ) -> 'None':
    """ Inserts a batch of realistic decisions into one hour bucket.
    """
    decisions = []

    for index in range(count):
        story = {
            'input': {'credit_score': 720},
            'output': {'approved': True},
        }
        decision = DecisionWrite(
            decision_id=f'{decision_id_prefix}-{index}',
            ruleset_id=ruleset_id,
            rules_version=1,
            occurred_at=occurred_at,
            business_key=f'application-{index}',
            outcome='approved',
            is_error=False,
            duration_ms=12,
            story=story,
            fired_rule_ids=['loans_Preferential_rate'],
        )
        decisions.append(decision)

    capture_policy = CapturePolicy()
    _ = backend.decisions.insert_batch(decisions, capture_policy)

# ################################################################################################################################
# ################################################################################################################################
