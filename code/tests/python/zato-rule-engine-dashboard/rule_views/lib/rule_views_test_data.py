# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Test_Set, \
    Definition_Type_Vocabulary, Documents_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

Author = 'anna.k'

# Flat terms evaluate directly against flat input mappings - this text backs every evaluation test.
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

# The same rule with a lower bar - version two in the version and diff tests.
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

# Dotted terms match the vocabulary's entity.attribute paths - this text backs the semantic tests.
Rules_Text_Dotted = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
when
    customer.creditScore is at least 700
then
    loan.rate = 2.9
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

def vocabulary_document() -> 'anydict':
    """ A small loan vocabulary covering numbers, choices and yes/no terms.
    """
    out = {
        'name': 'Loan approval',
        'entities': [
            {'name': 'customer', 'attributes': [
                {'name': 'creditScore', 'type': 'number range', 'domain': {'low': 300, 'high': 850},
                 'phrase': "the customer's credit score", 'status': ''},
                {'name': 'category', 'type': 'choice', 'values': ['Gold', 'Silver', 'Platinum'],
                 'phrase': "the customer's category", 'status': ''},
                {'name': 'segment', 'type': 'choice', 'values': ['Retail', 'Private'],
                 'phrase': "the customer's segment", 'status': 'deprecated'},
            ]},
            {'name': 'loan', 'attributes': [
                {'name': 'rate', 'type': 'number', 'phrase': 'the interest rate', 'status': ''},
                {'name': 'approved', 'type': 'yes/no', 'phrase': 'the loan is approved', 'status': ''},
            ]},
        ],
    }

    return out

# ################################################################################################################################

def suite_document() -> 'anydict':
    """ Two scenarios over the flat rules text - one asserting, one exploring.
    """
    out = {
        'name': 'Loan suite',
        'scenarios': [
            {
                'name': 'High score gets the rate',
                'input': {'credit_score': 720},
                'expected': {'rate': 2.9, 'approved': True},
            },
            {
                'name': 'Low score explores',
                'input': {'credit_score': 500},
                'expected': {},
            },
        ],
    }

    return out

# ################################################################################################################################

def table_document() -> 'anydict':
    """ A small decision table over credit scores and categories.
    """
    out = {
        'name': 'Loan approval',
        'docs': 'Approval decisions per credit score and category.',
        'filter': {'subject': 'amount', 'cell': '> 0'},
        'conditions': [
            {'letter': 'a', 'subject': 'credit_score'},
            {'letter': 'b', 'subject': 'category'},
        ],
        'actions': [
            {'target': 'approved'},
            {'target': 'rate'},
        ],
        'columns': [
            {
                'number': 0,
                'cells': {},
                'actions': {'rate': '4.5'},
                'statement': {'text': 'Every loan starts at the standard rate.', 'severity': 'info'},
            },
            {
                'number': 1,
                'cells': {'a': '700..850', 'b': 'in {Gold, Platinum}'},
                'actions': {'approved': 'true', 'rate': '2.9'},
                'statement': {'text': 'Top customers get the preferential rate.', 'severity': 'info'},
            },
            {
                'number': 2,
                'cells': {'a': '< 500'},
                'actions': {'approved': 'false'},
                'statement': {'text': 'Low scores are declined.', 'severity': 'violation'},
            },
        ],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def create_ruleset(
    backend:'RuleSQLBackend',
    name:'str'='Loans',
    text:'str'=Rules_Text,
    ruleset_name:'str'='loans',
    ) -> 'RuleDefinitionRecord':
    """ Stores one canonical ruleset definition.
    """
    documents = parse_documents(text, ruleset_name)

    out = backend.definitions.create(
        name=name,
        object_type=Definition_Type_Ruleset,
        document={Documents_Key: documents},
        author=Author,
        comment='Create the ruleset',
    )

    return out

# ################################################################################################################################

def create_vocabulary(backend:'RuleSQLBackend', name:'str'='Loan approval') -> 'RuleDefinitionRecord':
    """ Stores the shared vocabulary document.
    """
    out = backend.definitions.create(
        name=name,
        object_type=Definition_Type_Vocabulary,
        document=vocabulary_document(),
        author=Author,
        comment='Create the vocabulary',
    )

    return out

# ################################################################################################################################

def create_test_set(backend:'RuleSQLBackend', name:'str'='Loan suite') -> 'RuleDefinitionRecord':
    """ Stores the shared test-set document.
    """
    out = backend.definitions.create(
        name=name,
        object_type=Definition_Type_Test_Set,
        document=suite_document(),
        author=Author,
        comment='Create the test suite',
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
