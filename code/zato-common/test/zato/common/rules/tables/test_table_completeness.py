# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rules.table_completeness import check_completeness

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

def _new_table(conditions:'dictlist', columns:'dictlist') -> 'anydict':
    """ Builds a table with the given condition rows and rule columns.
    """
    out = {
        'name': 'Loan approval',
        'docs': '',
        'conditions': conditions,
        'actions': [
            {'target': 'approved'},
        ],
        'columns': columns,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCheckCompleteness(unittest.TestCase):
    """ Tests the cross-product completeness check and its proposed columns.
    """

    def test_uncovered_text_complement_is_missing(self) -> 'None':
        """ Categories no column handles come back as one missing not in combination.
        """
        conditions = [{'letter': 'a', 'subject': 'category'}]
        columns = [
            {'number': 1, 'cells': {'a': 'Gold'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': 'Silver'}, 'actions': {'approved': 'false'}},
        ]
        result = check_completeness(_new_table(conditions, columns))

        missing = result['missing']
        self.assertEqual(len(missing), 1)

        entry = missing[0]
        self.assertDictEqual(entry['cells'], {'a': 'not in {Gold, Silver}'})

        # The proposal numbers past the highest column and deliberately assigns nothing.
        proposed = result['proposed']
        self.assertEqual(len(proposed), 1)

        proposal = proposed[0]
        self.assertEqual(proposal['number'], 3)
        self.assertDictEqual(proposal['cells'], {'a': 'not in {Gold, Silver}'})
        self.assertDictEqual(proposal['actions'], {})

# ################################################################################################################################

    def test_numeric_split_covering_the_line_is_complete(self) -> 'None':
        """ Two comparisons that jointly cover every number leave nothing missing.
        """
        conditions = [{'letter': 'a', 'subject': 'credit_score'}]
        columns = [
            {'number': 1, 'cells': {'a': '< 500'}, 'actions': {'approved': 'false'}},
            {'number': 2, 'cells': {'a': '>= 500'}, 'actions': {'approved': 'true'}},
        ]
        result = check_completeness(_new_table(conditions, columns))

        self.assertListEqual(result['missing'], [])
        self.assertListEqual(result['proposed'], [])

# ################################################################################################################################

    def test_cross_product_of_two_rows(self) -> 'None':
        """ With two rows, every combination one column does not cover is missing.
        """
        conditions = [
            {'letter': 'a', 'subject': 'category'},
            {'letter': 'b', 'subject': 'is_member'},
        ]
        columns = [
            {'number': 1, 'cells': {'a': 'Gold', 'b': 'true'}, 'actions': {'approved': 'true'}},
        ]
        result = check_completeness(_new_table(conditions, columns))

        # The complement of one boolean value is the other bare word.
        missing = result['missing']
        self.assertEqual(len(missing), 3)

        first = missing[0]
        second = missing[1]
        third = missing[2]

        self.assertDictEqual(first['cells'], {'a': 'Gold', 'b': 'false'})
        self.assertDictEqual(second['cells'], {'a': 'not in {Gold}', 'b': 'true'})
        self.assertDictEqual(third['cells'], {'a': 'not in {Gold}', 'b': 'false'})

# ################################################################################################################################

    def test_blank_cells_cover_whole_rows(self) -> 'None':
        """ A column blank on a row covers everything the row can hold, complement included.
        """
        conditions = [
            {'letter': 'a', 'subject': 'category'},
            {'letter': 'b', 'subject': 'is_member'},
        ]
        columns = [
            {'number': 1, 'cells': {'a': 'Gold', 'b': 'true'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'b': 'false'}, 'actions': {'approved': 'false'}},
            {'number': 3, 'cells': {'a': 'not in {Gold}'}, 'actions': {'approved': 'false'}},
        ]
        result = check_completeness(_new_table(conditions, columns))

        self.assertListEqual(result['missing'], [])

# ################################################################################################################################

    def test_wider_cell_covers_narrower_alternatives(self) -> 'None':
        """ Coverage is provable from constraints, not just from equal cell texts.
        """
        conditions = [{'letter': 'a', 'subject': 'credit_score'}]
        columns = [
            {'number': 1, 'cells': {'a': '700..850'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': '>= 0'}, 'actions': {'approved': 'false'}},
        ]
        result = check_completeness(_new_table(conditions, columns))

        # The range is covered by the wider comparison, only the negatives are missing.
        missing = result['missing']
        self.assertEqual(len(missing), 1)

        entry = missing[0]
        self.assertDictEqual(entry['cells'], {'a': 'not (700..850, >= 0)'})

# ################################################################################################################################

    def test_unconstrained_table_is_complete(self) -> 'None':
        """ A table whose columns constrain nothing has nothing to miss.
        """
        conditions = [{'letter': 'a', 'subject': 'category'}]
        columns = [
            {'number': 1, 'cells': {}, 'actions': {'approved': 'true'}},
        ]
        result = check_completeness(_new_table(conditions, columns))

        self.assertListEqual(result['missing'], [])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
