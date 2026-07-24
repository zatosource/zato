# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, OK

# ################################################################################################################################

from rule_views_client import post_json
from rule_views_test_data import table_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def test_validate_accepts_a_clean_table(client:'any_') -> 'None':
    """ A well-formed table has no findings.
    """
    response = post_json(client, '/rules/tables/validate/', {'table': table_document()})
    assert response.status_code == OK
    assert response.json()['errors'] == []

# ################################################################################################################################

def test_validate_reports_a_broken_cell(client:'any_') -> 'None':
    """ A cell the grammar cannot accept is reported, never silently skipped.
    """
    table = table_document()
    table['columns'][1]['cells']['a'] = '700..'

    response = post_json(client, '/rules/tables/validate/', {'table': table})
    assert response.status_code == OK

    errors = response.json()['errors']
    assert len(errors) > 0

# ################################################################################################################################

def test_compile_produces_one_document_per_column(client:'any_') -> 'None':
    """ The compiler answers with the matchable rule form, column 0 first.
    """
    response = post_json(client, '/rules/tables/compile/', {'table': table_document()})
    assert response.status_code == OK

    documents = response.json()['documents']
    names = list(documents)
    assert names == ['Loan_approval_column_0', 'Loan_approval_column_1', 'Loan_approval_column_2']

# ################################################################################################################################

def test_compile_refuses_a_broken_table(client:'any_') -> 'None':
    """ A structurally broken table never reaches the compiler.
    """
    table = table_document()
    table['columns'][1]['cells']['a'] = '700..'

    response = post_json(client, '/rules/tables/compile/', {'table': table})
    assert response.status_code == BAD_REQUEST
    assert response.json()['errors']

# ################################################################################################################################

def test_checks_answer_in_one_payload(client:'any_') -> 'None':
    """ Completeness, conflicts, subsumption and unreachable come back together.
    """
    response = post_json(client, '/rules/tables/checks/', {'table': table_document()})
    assert response.status_code == OK

    data = response.json()
    assert 'completeness' in data
    assert 'conflicts' in data
    assert 'subsumption' in data
    assert 'unreachable' in data

# ################################################################################################################################

def test_expand_and_compress(client:'any_') -> 'None':
    """ A table expands into dotted sub-rules and compresses back into fewer columns.
    """
    response = post_json(client, '/rules/tables/expand/', {'table': table_document()})
    assert response.status_code == OK
    assert response.json()['documents']

    response = post_json(client, '/rules/tables/compress/', {'table': table_document()})
    assert response.status_code == OK

    compressed = response.json()['table']
    assert compressed['name'] == 'Loan approval'

# ################################################################################################################################
# ################################################################################################################################
