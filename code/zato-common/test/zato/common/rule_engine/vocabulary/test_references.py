# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.references import Role, extract_references, referenced_terms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# Two rules sharing terms - one compares against a reference and a membership list,
# the other uses a default, so every place a term can appear is covered.
_rules_text = """
rule
    Preferential_rate
defaults
    min_score = 700
when
    customer.creditScore is at least default.min_score and
    customer.category is one of 'Gold', 'Platinum' and
    loan.amount is less than customer.limit
then
    loan.rate = 2.9
    loan.handler = customer.category
else
    loan.rate = 4.5

rule
    Standard_rate
when
    customer.category is 'Standard'
then
    loan.rate = 3.9
"""

# ################################################################################################################################

def _get_documents() -> 'anydict':
    """ Parses the shared rules text into documents keyed by full name.
    """
    documents, errors = parse_data_details(_rules_text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################
# ################################################################################################################################

class TestExtractReferences(unittest.TestCase):
    """ Tests reference extraction from rule documents.
    """

    def setUp(self) -> 'None':
        self.documents = _get_documents()

# ################################################################################################################################

    def test_extract_covers_every_place(self) -> 'None':
        """ Subjects, value references and action targets are all extracted with their block and role.
        """
        document = self.documents['loans_Preferential_rate']
        usages = extract_references(document)

        self.assertIn({'term': 'customer.creditScore', 'block': 'when', 'role': Role.Subject}, usages)
        self.assertIn({'term': 'customer.limit', 'block': 'when', 'role': Role.Value}, usages)
        self.assertIn({'term': 'loan.rate', 'block': 'then', 'role': Role.Target}, usages)
        self.assertIn({'term': 'customer.category', 'block': 'then', 'role': Role.Value}, usages)
        self.assertIn({'term': 'loan.rate', 'block': 'else', 'role': Role.Target}, usages)

# ################################################################################################################################

    def test_default_references_are_not_terms(self) -> 'None':
        """ A reference to a rule-local default never counts as a vocabulary term.
        """
        document = self.documents['loans_Preferential_rate']

        terms = referenced_terms(document)
        self.assertNotIn('default.min_score', terms)
        self.assertNotIn('min_score', terms)

# ################################################################################################################################

    def test_referenced_terms_are_sorted_and_unique(self) -> 'None':
        """ The term list is sorted and free of duplicates even when a term appears in several places.
        """
        document = self.documents['loans_Preferential_rate']

        terms = referenced_terms(document)
        expected = ['customer.category', 'customer.creditScore', 'customer.limit', 'loan.amount', 'loan.handler', 'loan.rate']
        self.assertListEqual(terms, expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
