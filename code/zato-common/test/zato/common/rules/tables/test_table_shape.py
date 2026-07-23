# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rules.table import parse_cell
from zato.common.rules.table_shape import compress_table, expand_column, expand_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

def _new_table(columns:'dictlist') -> 'anydict':
    """ Builds a table with the shared rows and the given rule columns.
    """
    out = {
        'name': 'Loan approval',
        'docs': '',
        'conditions': [
            {'letter': 'a', 'subject': 'category'},
            {'letter': 'b', 'subject': 'credit_score'},
        ],
        'actions': [
            {'target': 'approved'},
        ],
        'columns': columns,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestExpand(unittest.TestCase):
    """ Tests expansion of multi-value cells into dotted sub-rules.
    """

    def test_membership_cell_expands_per_member(self) -> 'None':
        """ A two-member set expands into sub-rules 2.1 and 2.2, other cells untouched.
        """
        column = {'number': 2, 'cells': {'a': 'in {Gold, Platinum}', 'b': '>= 700'}, 'actions': {'approved': 'true'}}
        table = _new_table([column])

        expanded = expand_column(table, column)
        self.assertEqual(len(expanded), 2)

        first = expanded[0]
        second = expanded[1]

        self.assertEqual(first['number'], '2.1')
        self.assertEqual(second['number'], '2.2')

        self.assertDictEqual(first['cells'], {'a': "'Gold'", 'b': '>= 700'})
        self.assertDictEqual(second['cells'], {'a': "'Platinum'", 'b': '>= 700'})

        # Both sub-rules keep their column's actions.
        self.assertDictEqual(first['actions'], {'approved': 'true'})

# ################################################################################################################################

    def test_expanded_cells_parse_back(self) -> 'None':
        """ Every cell an expansion produces is valid cell syntax.
        """
        column = {'number': 1, 'cells': {'a': 'in {Gold, Platinum}'}, 'actions': {'approved': 'true'}}
        table = _new_table([column])

        for sub_column in expand_column(table, column):
            for cell_text in sub_column['cells'].values():
                result = parse_cell(cell_text)
                self.assertEqual(result.error, '', cell_text)

# ################################################################################################################################

    def test_two_multi_value_cells_cross_multiply(self) -> 'None':
        """ Two multi-value cells expand into the full cross product of their members.
        """
        column = {'number': 1, 'cells': {'a': 'in {Gold, Platinum}', 'b': 'in {700, 800}'}, 'actions': {'approved': 'true'}}
        table = _new_table([column])

        expanded = expand_column(table, column)
        self.assertEqual(len(expanded), 4)

        numbers = []
        for sub_column in expanded:
            numbers.append(sub_column['number'])

        self.assertListEqual(numbers, ['1.1', '1.2', '1.3', '1.4'])

# ################################################################################################################################

    def test_single_value_column_stays_whole(self) -> 'None':
        """ A column without multi-value cells comes back as itself, its number now a text.
        """
        column = {'number': 3, 'cells': {'a': 'Gold'}, 'actions': {'approved': 'true'}}
        table = _new_table([column])

        expanded = expand_column(table, column)
        self.assertEqual(len(expanded), 1)

        entry = expanded[0]
        self.assertEqual(entry['number'], '3')
        self.assertDictEqual(entry['cells'], {'a': 'Gold'})

# ################################################################################################################################

    def test_expand_table_walks_every_column(self) -> 'None':
        """ Expanding a table expands each rule column in number order.
        """
        columns = [
            {'number': 1, 'cells': {'a': 'in {Gold, Platinum}'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': 'Standard'}, 'actions': {'approved': 'false'}},
        ]
        expanded = expand_table(_new_table(columns))

        numbers = []
        for sub_column in expanded:
            numbers.append(sub_column['number'])

        self.assertListEqual(numbers, ['1.1', '1.2', '2'])

# ################################################################################################################################
# ################################################################################################################################

class TestCompress(unittest.TestCase):
    """ Tests merging of columns back into multi-value cells.
    """

    def test_columns_differing_in_one_row_merge(self) -> 'None':
        """ Same actions and one differing row merge into a membership cell.
        """
        columns = [
            {'number': 1, 'cells': {'a': 'Gold', 'b': '>= 700'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': 'Platinum', 'b': '>= 700'}, 'actions': {'approved': 'true'}},
        ]
        compressed = compress_table(_new_table(columns))

        merged_columns = compressed['columns']
        self.assertEqual(len(merged_columns), 1)

        merged = merged_columns[0]
        self.assertEqual(merged['number'], 1)
        self.assertDictEqual(merged['cells'], {'a': "in {'Gold', 'Platinum'}", 'b': '>= 700'})

        # The merged cell is valid cell syntax.
        result = parse_cell(merged['cells']['a'])
        self.assertEqual(result.error, '')

# ################################################################################################################################

    def test_merging_repeats_until_done(self) -> 'None':
        """ Three one-member columns collapse into a single three-member cell.
        """
        columns = [
            {'number': 1, 'cells': {'a': 'Gold'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': 'Platinum'}, 'actions': {'approved': 'true'}},
            {'number': 3, 'cells': {'a': 'Silver'}, 'actions': {'approved': 'true'}},
        ]
        compressed = compress_table(_new_table(columns))

        merged_columns = compressed['columns']
        self.assertEqual(len(merged_columns), 1)

        merged = merged_columns[0]
        self.assertDictEqual(merged['cells'], {'a': "in {'Gold', 'Platinum', 'Silver'}"})

# ################################################################################################################################

    def test_different_actions_never_merge(self) -> 'None':
        """ Columns assigning different values stay separate, renumbered in order.
        """
        columns = [
            {'number': 1, 'cells': {'a': 'Gold'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': 'Platinum'}, 'actions': {'approved': 'false'}},
        ]
        compressed = compress_table(_new_table(columns))

        merged_columns = compressed['columns']
        self.assertEqual(len(merged_columns), 2)

# ################################################################################################################################

    def test_column_zero_is_untouched(self) -> 'None':
        """ Compression leaves the action-only column exactly where and as it was.
        """
        columns = [
            {'number': 0, 'cells': {}, 'actions': {'approved': 'false'}},
            {'number': 1, 'cells': {'a': 'Gold'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': 'Platinum'}, 'actions': {'approved': 'true'}},
        ]
        compressed = compress_table(_new_table(columns))

        merged_columns = compressed['columns']
        self.assertEqual(len(merged_columns), 2)

        first = merged_columns[0]
        second = merged_columns[1]

        self.assertEqual(first['number'], 0)
        self.assertDictEqual(first['actions'], {'approved': 'false'})
        self.assertEqual(second['number'], 1)

# ################################################################################################################################

    def test_columns_differing_in_two_rows_never_merge(self) -> 'None':
        """ Columns that differ in more than one row are different rules, not one set.
        """
        columns = [
            {'number': 1, 'cells': {'a': 'Gold', 'b': '>= 700'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': 'Platinum', 'b': '>= 800'}, 'actions': {'approved': 'true'}},
        ]
        compressed = compress_table(_new_table(columns))

        merged_columns = compressed['columns']
        self.assertEqual(len(merged_columns), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
