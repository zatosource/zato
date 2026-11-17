# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_author = 'anna.k'

_rules_text = """
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

# ################################################################################################################################
# ################################################################################################################################

def _documents() -> 'anydict':
    """ Parses the shared rules text into canonical documents keyed by full name.
    """
    documents, errors = parse_data_details(_rules_text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################

def _create_ruleset(backend:'RuleSQLBackend', name:'str' = 'Loans') -> 'RuleDefinitionRecord':
    """ Stores one canonical ruleset definition.
    """
    out = backend.definitions.create(
        name=name,
        object_type=Definition_Type_Ruleset,
        document={Documents_Key: _documents()},
        author=_author,
        comment='Create the ruleset',
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_content_search_finds_rendered_sentences(backend:'RuleSQLBackend') -> 'None':
    """ Search matches the sentences a person reads and reports where the match is.
    """
    definition = _create_ruleset(backend)

    # A one-token search finds the term inside a rendered condition ..
    hits = backend.search.search('credit_score')
    assert len(hits) > 0

    hit = hits[0]
    assert hit['definition_id'] == definition.id
    assert hit['definition_name'] == 'Loans'
    assert hit['rule'] == 'loans_Preferential_rate'

    # .. the whole rendered line comes back with the match position inside it ..
    line = hit['line']
    start = hit['match_start']
    end = hit['match_end']
    assert line[start:end] == 'credit_score'
    assert 'is at least 700' in line

    # .. a search with spaces matches the rendered sentence, not the stored JSON ..
    sentence_hits = backend.search.search('at least 700')
    assert len(sentence_hits) == 1

    # .. the search is case-insensitive ..
    upper_hits = backend.search.search('CREDIT_SCORE')
    assert len(upper_hits) == len(hits)

    # .. and text nothing contains finds nothing.
    assert backend.search.search('no_such_text_anywhere') == []

# ################################################################################################################################
# ################################################################################################################################
