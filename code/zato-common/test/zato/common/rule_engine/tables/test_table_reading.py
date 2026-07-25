# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rule_engine.table_reading import CellReading, cell_reading, table_readings

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

def _get_table() -> 'anydict':
    """ A small table whose cells cover every reading there is.
    """
    out = {
        'name': 'Loan approval',
        'docs': '',
        'conditions': [
            {'letter': 'a', 'subject': 'credit_score'},
            {'letter': 'b', 'subject': 'category'},
        ],
        'actions': [
            {'target': 'approved'},
        ],
        'columns': [
            {
                'number': 0,
                'cells': {},
                'actions': {'approved': 'false'},
                'statement': {'text': '', 'severity': 'info'},
            },
            {
                'number': 1,
                'cells': {'a': '700..850', 'b': 'in {Gold, Platinum}'},
                'actions': {'approved': 'true'},
                'statement': {'text': '', 'severity': 'info'},
            },
            {
                'number': 2,
                'cells': {'a': '< 500', 'b': '-'},
                'actions': {'approved': 'false'},
                'statement': {'text': '', 'severity': 'info'},
            },
        ],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCellReading(unittest.TestCase):
    """ How one cell reads back, which is the only reading of cell syntax there is.
    """

# ################################################################################################################################

    def test_an_empty_cell_takes_no_part(self) -> 'None':
        """ Both ways of opting out of a column read the same.
        """
        self.assertEqual(cell_reading(''), {'kind': CellReading.Any})
        self.assertEqual(cell_reading('-'), {'kind': CellReading.Any})

# ################################################################################################################################

    def test_a_range_keeps_both_ends_as_numbers(self) -> 'None':
        """ A range reads back with its ends, and a number stays a number so it can be formatted as one.
        """
        reading = cell_reading('700..850')
        self.assertEqual(reading, {'kind': CellReading.Range, 'low': 700, 'high': 850})

# ################################################################################################################################

    def test_a_bare_number_is_equality_not_a_range(self) -> 'None':
        """ A cell naming one value compares against it - this is where a reading of its own used to disagree.
        """
        reading = cell_reading('700')
        self.assertEqual(reading, {'kind': CellReading.Comparison, 'symbol': '==', 'value': 700})

# ################################################################################################################################

    def test_set_membership_carries_its_members(self) -> 'None':
        """ Both forms of membership read back with their members, unquoted the way authors write them.
        """
        reading = cell_reading('in {Gold, Platinum}')
        self.assertEqual(reading, {'kind': CellReading.Set, 'items': ['Gold', 'Platinum'], 'negated': False})

        reading = cell_reading('not in {Gold}')
        self.assertEqual(reading, {'kind': CellReading.Set, 'items': ['Gold'], 'negated': True})

# ################################################################################################################################

    def test_a_quoted_member_keeps_its_comma(self) -> 'None':
        """ A comma inside a quoted member belongs to that member rather than separating two of them.
        """
        reading = cell_reading("in {'Gold, Platinum', Silver}")
        self.assertEqual(reading, {'kind': CellReading.Set, 'items': ['Gold, Platinum', 'Silver'], 'negated': False})

# ################################################################################################################################

    def test_a_leading_symbol_reads_as_that_comparison(self) -> 'None':
        """ Every symbol a cell may open with reads back as the symbol it was written with.
        """
        reading = cell_reading('< 500')
        self.assertEqual(reading, {'kind': CellReading.Comparison, 'symbol': '<', 'value': 500})

        reading = cell_reading('>= 18')
        self.assertEqual(reading, {'kind': CellReading.Comparison, 'symbol': '>=', 'value': 18})

# ################################################################################################################################

    def test_a_quoted_value_holding_dots_is_not_a_range(self) -> 'None':
        """ Quoted text never opens a range, and it reads back without its quotes.
        """
        reading = cell_reading("'700..850'")
        self.assertEqual(reading, {'kind': CellReading.Comparison, 'symbol': '==', 'value': '700..850'})

# ################################################################################################################################

    def test_a_dotted_word_reads_as_the_term_it_points_to(self) -> 'None':
        """ A dotted bare word is a reference to another term, an undotted one is enumeration text.
        """
        reading = cell_reading('customer.limit')
        self.assertEqual(reading, {'kind': CellReading.Comparison, 'symbol': '==', 'value': 'customer.limit'})

        reading = cell_reading('Gold')
        self.assertEqual(reading, {'kind': CellReading.Comparison, 'symbol': '==', 'value': 'Gold'})

# ################################################################################################################################

    def test_text_the_grammar_does_not_read_says_so(self) -> 'None':
        """ An unreadable cell reads back as itself, so a screen can show what was typed.
        """
        reading = cell_reading('700..')
        self.assertEqual(reading, {'kind': CellReading.Unreadable, 'text': '700..'})

# ################################################################################################################################
# ################################################################################################################################

class TestTableReadings(unittest.TestCase):
    """ How a whole table reads back, which is what one validation answer carries.
    """

# ################################################################################################################################

    def test_every_condition_cell_is_read_by_column_number(self) -> 'None':
        """ The readings are keyed by column number and condition letter, the coordinates a grid has.
        """
        readings = table_readings(_get_table())

        self.assertEqual(sorted(readings), ['0', '1', '2'])
        self.assertEqual(readings['0'], {})

        self.assertEqual(readings['1']['a'], {'kind': CellReading.Range, 'low': 700, 'high': 850})
        self.assertEqual(readings['1']['b'], {'kind': CellReading.Set, 'items': ['Gold', 'Platinum'], 'negated': False})

        self.assertEqual(readings['2']['a'], {'kind': CellReading.Comparison, 'symbol': '<', 'value': 500})
        self.assertEqual(readings['2']['b'], {'kind': CellReading.Any})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
