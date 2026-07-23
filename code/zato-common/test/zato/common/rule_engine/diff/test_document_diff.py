# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rule_engine.diff import diff_documents
from zato.common.rule_engine.parser import parse_data_details

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The old version of a small ruleset - two rules that the tests evolve in various ways.
_old_text = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
defaults
    min_score = 700
when
    customer.creditScore is at least default.min_score and
    customer.category is one of 'Gold', 'Platinum'
then
    loan.rate = 2.9
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

def _parse(text:'str') -> 'anydict':
    """ Parses rules text into documents keyed by full name.
    """
    documents, errors = parse_data_details(text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################
# ################################################################################################################################

class TestDiffBuckets(unittest.TestCase):
    """ Tests that the diff groups rules into the right buckets.
    """

    def setUp(self) -> 'None':
        self.old_documents = _parse(_old_text)

# ################################################################################################################################

    def test_identical_rulesets_are_all_unchanged(self) -> 'None':
        """ Comparing a ruleset with itself reports every rule as unchanged and nothing else.
        """
        new_documents = _parse(_old_text)
        result = diff_documents(self.old_documents, new_documents)

        self.assertListEqual(result['added'], [])
        self.assertListEqual(result['deleted'], [])
        self.assertListEqual(result['renamed'], [])
        self.assertListEqual(result['updated'], [])

        unchanged = result['unchanged']
        self.assertEqual(len(unchanged), 2)

        first = unchanged[0]
        second = unchanged[1]
        self.assertEqual(first['rule'], 'loans_Preferential_rate')
        self.assertEqual(second['rule'], 'loans_Standard_rate')

# ################################################################################################################################

    def test_reformatting_produces_no_noise(self) -> 'None':
        """ Comments, blank lines and value spacing are not changes - the diff is structural, never textual.
        """
        reformatted = """
# Rates for preferential customers.

rule
    Preferential_rate

docs
    Better rates for our best customers.
defaults
    min_score   =   700
when
    customer.creditScore   is at least   default.min_score    and
    customer.category is one of 'Gold','Platinum'
then
    loan.rate =    2.9
else
    loan.rate = 4.5


rule
    Standard_rate
when
    customer.category is 'Standard'   # Only the standard category.
then
    loan.rate = 3.9
"""
        new_documents = _parse(reformatted)
        result = diff_documents(self.old_documents, new_documents)

        self.assertListEqual(result['added'], [])
        self.assertListEqual(result['deleted'], [])
        self.assertListEqual(result['renamed'], [])
        self.assertListEqual(result['updated'], [])
        self.assertEqual(len(result['unchanged']), 2)

# ################################################################################################################################

    def test_added_and_deleted_rules(self) -> 'None':
        """ A rule only in the new version is added, one only in the old version is deleted.
        """
        new_text = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
defaults
    min_score = 700
when
    customer.creditScore is at least default.min_score and
    customer.category is one of 'Gold', 'Platinum'
then
    loan.rate = 2.9
else
    loan.rate = 4.5

rule
    Manual_review
when
    loan.amount is more than 100000
then
    loan.needs_review = true
"""
        new_documents = _parse(new_text)
        result = diff_documents(self.old_documents, new_documents)

        added = result['added']
        deleted = result['deleted']

        self.assertEqual(len(added), 1)
        self.assertEqual(len(deleted), 1)

        added_entry = added[0]
        deleted_entry = deleted[0]

        self.assertEqual(added_entry['rule'], 'loans_Manual_review')
        self.assertEqual(deleted_entry['rule'], 'loans_Standard_rate')

        # Every entry carries its rendered canonical form.
        self.assertIn('loan.needs_review = true', added_entry['rendered'])
        self.assertIn("customer.category is 'Standard'", deleted_entry['rendered'])

        self.assertListEqual(result['renamed'], [])
        self.assertListEqual(result['updated'], [])
        self.assertEqual(len(result['unchanged']), 1)

# ################################################################################################################################
# ################################################################################################################################

class TestDiffUpdated(unittest.TestCase):
    """ Tests that updated rules name exactly the blocks that changed.
    """

    def setUp(self) -> 'None':
        self.old_documents = _parse(_old_text)

# ################################################################################################################################

    def _diff_with(self, new_text:'str') -> 'anydict':
        """ Diffs the shared old version against the given new text.
        """
        new_documents = _parse(new_text)
        out = diff_documents(self.old_documents, new_documents)
        return out

# ################################################################################################################################

    def test_condition_change_is_a_when_change(self) -> 'None':
        """ Changing a condition value names the when block and supplies both rendered forms.
        """
        new_text = _old_text.replace('is at least default.min_score', 'is at least 750')
        result = self._diff_with(new_text)

        updated = result['updated']
        self.assertEqual(len(updated), 1)

        entry = updated[0]
        self.assertEqual(entry['rule'], 'loans_Preferential_rate')
        self.assertListEqual(entry['changed'], ['when'])

        self.assertIn('default.min_score', entry['old_rendered'])
        self.assertIn('750', entry['new_rendered'])

# ################################################################################################################################

    def test_joiner_change_is_a_when_change(self) -> 'None':
        """ Swapping and for or, with the conditions untouched, is still a when change.
        """
        new_text = _old_text.replace('default.min_score and', 'default.min_score or')
        result = self._diff_with(new_text)

        updated = result['updated']
        self.assertEqual(len(updated), 1)

        entry = updated[0]
        self.assertListEqual(entry['changed'], ['when'])

# ################################################################################################################################

    def test_multiple_changed_blocks_are_all_named(self) -> 'None':
        """ A rule with edits across blocks names every changed block, in document order.
        """
        new_text = _old_text.replace('Better rates for our best customers.', 'Preferential pricing.')
        new_text = new_text.replace('min_score = 700', 'min_score = 720')
        new_text = new_text.replace('loan.rate = 2.9', 'loan.rate = 2.5')
        new_text = new_text.replace('loan.rate = 4.5', 'loan.rate = 4.9')

        result = self._diff_with(new_text)

        updated = result['updated']
        self.assertEqual(len(updated), 1)

        entry = updated[0]
        self.assertListEqual(entry['changed'], ['docs', 'defaults', 'then', 'else'])

# ################################################################################################################################
# ################################################################################################################################

class TestDiffRenames(unittest.TestCase):
    """ Tests that a renamed rule reads as a move, never as a delete plus an add.
    """

    def setUp(self) -> 'None':
        self.old_documents = _parse(_old_text)

# ################################################################################################################################

    def test_rename_is_a_move(self) -> 'None':
        """ The same content under a new name is one rename, not a delete and an add.
        """
        new_text = _old_text.replace('Standard_rate', 'Regular_rate')
        new_documents = _parse(new_text)
        result = diff_documents(self.old_documents, new_documents)

        self.assertListEqual(result['added'], [])
        self.assertListEqual(result['deleted'], [])

        renamed = result['renamed']
        self.assertEqual(len(renamed), 1)

        entry = renamed[0]
        self.assertEqual(entry['old_rule'], 'loans_Standard_rate')
        self.assertEqual(entry['new_rule'], 'loans_Regular_rate')
        self.assertIn("customer.category is 'Standard'", entry['rendered'])

# ################################################################################################################################

    def test_rename_with_content_change_is_not_a_move(self) -> 'None':
        """ A new name over changed content is a real delete plus a real add.
        """
        new_text = _old_text.replace('Standard_rate', 'Regular_rate')
        new_text = new_text.replace('loan.rate = 3.9', 'loan.rate = 4.1')
        new_documents = _parse(new_text)
        result = diff_documents(self.old_documents, new_documents)

        self.assertListEqual(result['renamed'], [])
        self.assertEqual(len(result['added']), 1)
        self.assertEqual(len(result['deleted']), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
