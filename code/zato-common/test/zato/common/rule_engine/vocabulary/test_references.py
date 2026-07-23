# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from copy import deepcopy

# Zato
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.references import Role, apply_rename, can_delete, extract_references, preview_rename, \
    referenced_terms, rename_term, where_used

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

class TestWhereUsed(unittest.TestCase):
    """ Tests the where-used answer across documents.
    """

    def setUp(self) -> 'None':
        self.documents = _get_documents()

# ################################################################################################################################

    def test_term_used_by_both_rules(self) -> 'None':
        """ A term shared by two rules reports usages in both.
        """
        usages = where_used('customer.category', self.documents)

        rules = set()
        for usage in usages:
            rules.add(usage['rule'])

        self.assertSetEqual(rules, {'loans_Preferential_rate', 'loans_Standard_rate'})

# ################################################################################################################################

    def test_term_used_nowhere(self) -> 'None':
        """ A term no rule references reports no usages.
        """
        usages = where_used('customer.height', self.documents)
        self.assertListEqual(usages, [])

# ################################################################################################################################

    def test_delete_blocked_while_used(self) -> 'None':
        """ Deletion is possible only for terms nothing references.
        """
        self.assertFalse(can_delete('customer.category', self.documents))
        self.assertTrue(can_delete('customer.height', self.documents))

# ################################################################################################################################
# ################################################################################################################################

class TestRename(unittest.TestCase):
    """ Tests rename as a document rewrite with a dry-run preview.
    """

    def setUp(self) -> 'None':
        self.documents = _get_documents()

# ################################################################################################################################

    def test_rename_rewrites_every_place(self) -> 'None':
        """ A rename changes the subject, the value reference and the assignment reference alike.
        """
        document = self.documents['loans_Preferential_rate']
        result = rename_term(document, 'customer.category', 'customer.tier')

        # The membership subject and the assignment reference change.
        self.assertEqual(result.change_count, 2)

        terms = referenced_terms(result.document)
        self.assertIn('customer.tier', terms)
        self.assertNotIn('customer.category', terms)

# ################################################################################################################################

    def test_rename_never_modifies_the_input(self) -> 'None':
        """ The rewrite happens on a copy - the original document stays as it was.
        """
        document = self.documents['loans_Preferential_rate']
        before = deepcopy(document)

        _ = rename_term(document, 'customer.category', 'customer.tier')
        self.assertDictEqual(document, before)

# ################################################################################################################################

    def test_rename_counts_each_target(self) -> 'None':
        """ A term written to in both branches counts each assignment it changes.
        """
        document = self.documents['loans_Preferential_rate']
        result = rename_term(document, 'loan.rate', 'loan.interest')

        # One then target and one else target change.
        self.assertEqual(result.change_count, 2)

# ################################################################################################################################

    def test_preview_reports_impact_per_rule(self) -> 'None':
        """ The dry-run preview names every affected rule with its change count and nothing else.
        """
        preview = preview_rename('customer.category', 'customer.tier', self.documents)

        counts = {}
        for entry in preview:
            counts[entry['rule']] = entry['change_count']

        self.assertDictEqual(counts, {'loans_Preferential_rate': 2, 'loans_Standard_rate': 1})

# ################################################################################################################################

    def test_preview_leaves_documents_unchanged(self) -> 'None':
        """ A preview is a dry run - no document changes.
        """
        before = deepcopy(self.documents)

        _ = preview_rename('customer.category', 'customer.tier', self.documents)
        self.assertDictEqual(self.documents, before)

# ################################################################################################################################

    def test_apply_returns_only_rewritten_documents(self) -> 'None':
        """ Applying a rename returns the rewritten documents only, keyed by full name.
        """
        rewritten = apply_rename('customer.limit', 'customer.ceiling', self.documents)

        self.assertListEqual(sorted(rewritten), ['loans_Preferential_rate'])

        terms = referenced_terms(rewritten['loans_Preferential_rate'])
        self.assertIn('customer.ceiling', terms)
        self.assertNotIn('customer.limit', terms)

# ################################################################################################################################

    def test_rename_of_unused_term_changes_nothing(self) -> 'None':
        """ Renaming a term nothing references rewrites no documents.
        """
        rewritten = apply_rename('customer.height', 'customer.stature', self.documents)
        self.assertDictEqual(rewritten, {})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
