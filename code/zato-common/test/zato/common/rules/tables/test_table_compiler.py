# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rules.api import RulesManager
from zato.common.rules.document import Comparator
from zato.common.rules.table import compile_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

def _get_table() -> 'anydict':
    """ Builds a small valid decision table - the same shape the validation tests use.
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

class TestCompileTable(unittest.TestCase):
    """ Tests the shape of the documents a table compiles into.
    """

    def setUp(self) -> 'None':
        self.table = _get_table()
        self.documents = compile_table(self.table)

# ################################################################################################################################

    def test_one_document_per_column_with_column_zero_first(self) -> 'None':
        """ Each column becomes one document, named after its number, with column 0 first.
        """
        names = list(self.documents)
        expected = ['Loan_approval_column_0', 'Loan_approval_column_1', 'Loan_approval_column_2']
        self.assertListEqual(names, expected)

# ################################################################################################################################

    def test_filter_gates_every_column(self) -> 'None':
        """ The filter compiles into the first condition of every document.
        """
        for document in self.documents.values():
            conditions = document['conditions']
            first = conditions[0]
            self.assertEqual(first['subject'], 'amount', document['name'])
            self.assertEqual(first['comparator'], Comparator.Is_More_Than, document['name'])

# ################################################################################################################################

    def test_column_conditions_join_with_and(self) -> 'None':
        """ A column's cells become conditions in row order, joined with and.
        """
        document = self.documents['Loan_approval_column_1']
        conditions = document['conditions']

        # The filter comes first, then the range row, then the set row.
        self.assertEqual(len(conditions), 3)

        range_condition = conditions[1]
        set_condition = conditions[2]

        self.assertEqual(range_condition['subject'], 'credit_score')
        self.assertEqual(range_condition['comparator'], Comparator.Is_Between)

        self.assertEqual(set_condition['subject'], 'category')
        self.assertEqual(set_condition['comparator'], Comparator.Is_One_Of)

        self.assertListEqual(document['joiners'], ['and', 'and'])

# ################################################################################################################################

    def test_actions_follow_row_order(self) -> 'None':
        """ Action cells become then assignments in action row order, skipping absent targets.
        """
        document = self.documents['Loan_approval_column_1']
        then = document['then']

        self.assertEqual(len(then), 2)

        first = then[0]
        second = then[1]

        self.assertEqual(first['target'], 'approved')
        self.assertEqual(second['target'], 'rate')

        rate_value = second['value']
        self.assertEqual(rate_value['value'], 2.9)

        # Column 2 leaves the rate alone so its then has only the approval.
        declined = self.documents['Loan_approval_column_2']
        declined_then = declined['then']
        self.assertEqual(len(declined_then), 1)

# ################################################################################################################################

    def test_statements_travel_with_documents(self) -> 'None':
        """ Each column's statement is carried on its compiled document.
        """
        document = self.documents['Loan_approval_column_2']
        statement = document['statement']

        self.assertEqual(statement['text'], 'Low scores are declined.')
        self.assertEqual(statement['severity'], 'violation')

# ################################################################################################################################

    def test_column_zero_without_filter_always_fires(self) -> 'None':
        """ Without a filter, column 0 compiles to one condition that never touches the input.
        """
        del self.table['filter']
        documents = compile_table(self.table)

        document = documents['Loan_approval_column_0']
        conditions = document['conditions']

        self.assertEqual(len(conditions), 1)

        condition = conditions[0]
        self.assertEqual(condition['subject'], 'true')
        self.assertEqual(condition['comparator'], Comparator.Is)

# ################################################################################################################################
# ################################################################################################################################

class TestCompiledTableRuns(unittest.TestCase):
    """ Tests that compiled documents load and match in the engine as any parsed rules do.
    """

    def setUp(self) -> 'None':
        self.table = _get_table()
        documents = compile_table(self.table)

        self.manager = RulesManager()
        _ = self.manager.load_parsed_rules(documents, 'Loan_approval')

# ################################################################################################################################

    def test_column_zero_fires_for_any_input_the_filter_admits(self) -> 'None':
        """ Column 0 fires whenever the filter admits the input, whatever the rest of it holds.
        """
        result = self.manager['Loan_approval_column_0'].match({'amount': 1000})
        self.assertTrue(result)
        self.assertEqual(result.then['rate'], 4.5)

# ################################################################################################################################

    def test_filter_blocks_the_whole_table(self) -> 'None':
        """ Input the filter rejects matches no column, not even the action-only one.
        """
        result = self.manager['Loan_approval_column_0'].match({'amount': 0})
        self.assertFalse(result)

# ################################################################################################################################

    def test_preferential_column_matches(self) -> 'None':
        """ A top customer matches column 1 and gets the preferential rate.
        """
        data = {'amount': 1000, 'credit_score': 720, 'category': 'Gold'}
        result = self.manager['Loan_approval_column_1'].match(data)

        self.assertTrue(result)
        self.assertEqual(result.then['approved'], True)
        self.assertEqual(result.then['rate'], 2.9)

# ################################################################################################################################

    def test_declining_column_matches(self) -> 'None':
        """ A low score matches column 2 and is declined.
        """
        data = {'amount': 1000, 'credit_score': 450, 'category': 'Standard'}
        result = self.manager['Loan_approval_column_2'].match(data)

        self.assertTrue(result)
        self.assertEqual(result.then['approved'], False)

# ################################################################################################################################

    def test_middle_scores_match_neither_lettered_column(self) -> 'None':
        """ A score between the bands matches neither column 1 nor column 2.
        """
        data = {'amount': 1000, 'credit_score': 600, 'category': 'Standard'}

        preferential = self.manager['Loan_approval_column_1'].match(data)
        declined = self.manager['Loan_approval_column_2'].match(data)

        self.assertFalse(preferential)
        self.assertFalse(declined)

# ################################################################################################################################

    def test_column_zero_without_filter_matches_empty_input(self) -> 'None':
        """ Without a filter, column 0 matches even empty input - no field has to exist for it.
        """
        del self.table['filter']
        documents = compile_table(self.table)

        manager = RulesManager()
        _ = manager.load_parsed_rules(documents, 'Loan_approval')

        result = manager['Loan_approval_column_0'].match({})
        self.assertTrue(result)
        self.assertEqual(result.then['rate'], 4.5)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
