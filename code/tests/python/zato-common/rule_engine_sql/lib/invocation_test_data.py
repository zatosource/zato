# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.invocation import RulesetInvoker, Vocabulary_Key
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

author = 'anna.k'

# One rule that fires on good scores - the first published version in every test.
rules_text = """
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

# The same rule with a lower bar - the second version in the republish tests.
rules_text_lower_bar = """
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

# Dotted terms match the vocabulary's entity.attribute paths - this text backs the validation tests.
rules_text_dotted = """
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

def documents_of(text:'str', ruleset_name:'str'='payments') -> 'anydict':
    """ Parses rules text into canonical documents, loud on any parse error.
    """
    documents, errors = parse_data_details(text, ruleset_name)
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################

def vocabulary_document() -> 'anydict':
    """ A small loan vocabulary covering a number range and outputs.
    """
    out = {
        'name': 'Loan approval',
        'entities': [
            {'name': 'customer', 'attributes': [
                {'name': 'creditScore', 'type': 'number range', 'domain': {'low': 300, 'high': 850},
                 'phrase': "the customer's credit score", 'status': ''},
            ]},
            {'name': 'loan', 'attributes': [
                {'name': 'rate', 'type': 'number', 'phrase': 'the interest rate', 'status': ''},
            ]},
        ],
    }

    return out

# ################################################################################################################################

def create_ruleset(
    backend:'RuleSQLBackend',
    name:'str' = 'payments.discounts',
    text:'str' = rules_text,
    parent_id:'int | None' = None,
    vocabulary_id:'int | None' = None,
    ) -> 'RuleDefinitionRecord':
    """ Stores one ruleset definition, optionally bound to a vocabulary.
    """
    document:'anydict' = {Documents_Key: documents_of(text)}

    if vocabulary_id:
        document[Vocabulary_Key] = vocabulary_id

    out = backend.definitions.create(
        name=name,
        object_type=Definition_Type_Ruleset,
        document=document,
        author=author,
        comment='Create the ruleset',
        parent_id=parent_id,
    )
    return out

# ################################################################################################################################

def publish(backend:'RuleSQLBackend', definition_id:'int', version:'int'=1) -> 'None':
    """ Makes one stored version live.
    """
    _ = backend.versions.publish(definition_id=definition_id, version=version, actor=author)

# ################################################################################################################################

def new_invoker(backend:'RuleSQLBackend') -> 'RulesetInvoker':
    """ Builds an invoker over the test backend - its caches are correct until `apply_change` evicts,
    exactly as the change stream listener does on a server.
    The tests enter `invoker.writer` as a context manager, which starts the writer and flushes it on exit.
    """
    writer = backend.decision_writer()

    out = RulesetInvoker(backend, writer)
    return out

# ################################################################################################################################
# ################################################################################################################################

class RecordingPublisher:
    """ Stands in for the Redis-backed change publisher, recording what would land on the stream.
    """
    def __init__(self) -> 'None':
        self.published = []

    def publish(self, kind:'str', definition_id:'int', name:'str', object_type:'str') -> 'None':
        self.published.append((kind, definition_id, name, object_type))

# ################################################################################################################################
# ################################################################################################################################
