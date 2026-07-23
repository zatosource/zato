# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rule_engine.document import Comparator, NodeKind
from zato.common.rule_engine.table import parse_cell, parse_cell_value, validate_table
from zato.common.rule_engine.vocabulary import ErrorCode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

def _get_table() -> 'anydict':
    """ Builds a small valid decision table the tests then break in various ways.
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
                'cells': {'a': '< 500', 'b': '-'},
                'actions': {'approved': 'false'},
                'statement': {'text': 'Low scores are declined.', 'severity': 'violation'},
            },
        ],
    }
    return out

# ################################################################################################################################

def _get_condition(text:'str') -> 'anydict':
    """ Parses a cell that has to produce a condition, failing loudly otherwise.
    """
    result = parse_cell(text)
    condition = result.condition

    if condition is None:
        raise Exception(f'No condition parsed from `{text}` -> `{result.error}`')

    return condition

# ################################################################################################################################

def _get_value(text:'str') -> 'anydict':
    """ Parses a cell value that has to be recognized, failing loudly otherwise.
    """
    node = parse_cell_value(text)

    if node is None:
        raise Exception(f'Not a recognized cell value -> `{text}`')

    return node

# ################################################################################################################################
# ################################################################################################################################

class TestParseCell(unittest.TestCase):
    """ Tests the cell syntax - ranges, sets, comparator symbols and plain values.
    """

    def test_blank_and_dash_opt_out(self) -> 'None':
        """ An empty cell and a lone dash both mean the condition takes no part.
        """
        for text in ('', '   ', '-'):
            result = parse_cell(text)
            self.assertIsNone(result.condition)
            self.assertEqual(result.error, '')

# ################################################################################################################################

    def test_plain_number_means_equality(self) -> 'None':
        """ A plain number compares with is.
        """
        condition = _get_condition('700')
        self.assertEqual(condition['comparator'], Comparator.Is)

        values = condition['values']
        value = values[0]
        self.assertEqual(value['value'], 700)

# ################################################################################################################################

    def test_bare_word_is_an_enumeration_text(self) -> 'None':
        """ A bare word without a dot is a string literal, not a reference.
        """
        condition = _get_condition('Gold')

        values = condition['values']
        value = values[0]
        self.assertEqual(value['kind'], NodeKind.Literal)
        self.assertEqual(value['value'], 'Gold')

# ################################################################################################################################

    def test_dotted_word_stays_a_reference(self) -> 'None':
        """ A dotted bare word keeps referring to another term.
        """
        node = _get_value('customer.limit')
        self.assertEqual(node['kind'], NodeKind.Reference)
        self.assertEqual(node['term'], 'customer.limit')

# ################################################################################################################################

    def test_range_becomes_is_between(self) -> 'None':
        """ A lower..upper cell compares with is between.
        """
        condition = _get_condition('18..65')
        self.assertEqual(condition['comparator'], Comparator.Is_Between)

        values = condition['values']
        lower = values[0]
        upper = values[1]
        self.assertEqual(lower['value'], 18)
        self.assertEqual(upper['value'], 65)

# ################################################################################################################################

    def test_set_membership(self) -> 'None':
        """ An in cell with braces compares with is one of, each member an enumeration text.
        """
        condition = _get_condition('in {MA, NH, VT}')
        self.assertEqual(condition['comparator'], Comparator.Is_One_Of)

        values = condition['values']
        self.assertEqual(len(values), 3)

        first = values[0]
        self.assertEqual(first['value'], 'MA')

# ################################################################################################################################

    def test_negated_set_membership(self) -> 'None':
        """ A not in cell compares with is not one of.
        """
        condition = _get_condition('not in {Gold, Platinum}')
        self.assertEqual(condition['comparator'], Comparator.Is_Not_One_Of)

# ################################################################################################################################

    def test_comparator_symbols(self) -> 'None':
        """ Each leading symbol maps to its canonical comparator.
        """
        expected = {
            '== 5': Comparator.Is,
            '!= 5': Comparator.Is_Not,
            '< 5': Comparator.Is_Less_Than,
            '<= 5': Comparator.Is_At_Most,
            '>= 5': Comparator.Is_At_Least,
            '> 5': Comparator.Is_More_Than,
        }

        for text, comparator in expected.items():
            condition = _get_condition(text)
            self.assertEqual(condition['comparator'], comparator, text)

# ################################################################################################################################

    def test_word_starting_with_in_is_not_the_keyword(self) -> 'None':
        """ A cell like inactive is a plain value, never the in keyword.
        """
        condition = _get_condition('inactive')
        self.assertEqual(condition['comparator'], Comparator.Is)

        values = condition['values']
        value = values[0]
        self.assertEqual(value['value'], 'inactive')

# ################################################################################################################################

    def test_quoted_text_with_dots_is_a_plain_value(self) -> 'None':
        """ A quoted string containing two dots is never mistaken for a range.
        """
        condition = _get_condition("'up..down'")
        self.assertEqual(condition['comparator'], Comparator.Is)

        values = condition['values']
        value = values[0]
        self.assertEqual(value['value'], 'up..down')

# ################################################################################################################################

    def test_bad_cells_report_errors(self) -> 'None':
        """ A set without braces, an empty set and an unrecognizable value all report errors.
        """
        for text in ('in Gold, Platinum', 'in {}', '>= ', '700..'):
            result = parse_cell(text)
            self.assertIsNone(result.condition, text)
            self.assertNotEqual(result.error, '', text)

# ################################################################################################################################
# ################################################################################################################################

class TestValidateTable(unittest.TestCase):
    """ Tests the structural checks over a whole decision table.
    """

    def setUp(self) -> 'None':
        self.table = _get_table()

# ################################################################################################################################

    def _get_codes(self) -> 'strlist':
        """ Validates the table and returns the codes of every finding.
        """
        errors = validate_table(self.table)

        out = []
        for error in errors:
            out.append(error['code'])

        return out

# ################################################################################################################################

    def test_valid_table_has_no_findings(self) -> 'None':
        """ The unbroken table validates cleanly.
        """
        errors = validate_table(self.table)
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_bad_row_letter(self) -> 'None':
        """ A row letter has to be one lowercase letter.
        """
        row = self.table['conditions'][0]
        row['letter'] = 'A'
        self.assertIn(ErrorCode.Bad_Row, self._get_codes())

# ################################################################################################################################

    def test_duplicate_row_letter(self) -> 'None':
        """ Two rows with the same letter are reported.
        """
        row = self.table['conditions'][1]
        row['letter'] = 'a'
        self.assertIn(ErrorCode.Duplicate_Row, self._get_codes())

# ################################################################################################################################

    def test_bad_row_subject(self) -> 'None':
        """ A subject has to be a recognizable identifier.
        """
        row = self.table['conditions'][0]
        row['subject'] = '9bad'
        self.assertIn(ErrorCode.Bad_Row, self._get_codes())

# ################################################################################################################################

    def test_duplicate_action_target(self) -> 'None':
        """ Two action rows with the same target are reported.
        """
        row = self.table['actions'][1]
        row['target'] = 'approved'
        self.assertIn(ErrorCode.Duplicate_Row, self._get_codes())

# ################################################################################################################################

    def test_duplicate_column_number(self) -> 'None':
        """ Two columns with the same number are reported.
        """
        column = self.table['columns'][2]
        column['number'] = 1
        self.assertIn(ErrorCode.Duplicate_Column, self._get_codes())

# ################################################################################################################################

    def test_negative_column_number(self) -> 'None':
        """ Column numbers count up from zero.
        """
        column = self.table['columns'][2]
        column['number'] = -1
        self.assertIn(ErrorCode.Bad_Column, self._get_codes())

# ################################################################################################################################

    def test_column_zero_takes_no_conditions(self) -> 'None':
        """ Column 0 is action-only so a condition cell in it is reported.
        """
        column = self.table['columns'][0]
        column['cells'] = {'a': '> 100'}
        self.assertIn(ErrorCode.Bad_Column, self._get_codes())

# ################################################################################################################################

    def test_other_columns_need_conditions(self) -> 'None':
        """ A non-zero column whose cells all opt out is reported.
        """
        column = self.table['columns'][2]
        column['cells'] = {'a': '-', 'b': ''}
        self.assertIn(ErrorCode.Bad_Column, self._get_codes())

# ################################################################################################################################

    def test_unknown_row_letter_in_cell(self) -> 'None':
        """ A cell in a row no letter names is reported.
        """
        column = self.table['columns'][1]
        column['cells']['z'] = '> 5'
        self.assertIn(ErrorCode.Bad_Cell, self._get_codes())

# ################################################################################################################################

    def test_unparseable_cell(self) -> 'None':
        """ A cell whose text does not parse is reported.
        """
        column = self.table['columns'][1]
        column['cells']['a'] = 'in Gold'
        self.assertIn(ErrorCode.Bad_Cell, self._get_codes())

# ################################################################################################################################

    def test_unknown_action_target(self) -> 'None':
        """ An action cell targeting an unknown row is reported.
        """
        column = self.table['columns'][1]
        column['actions']['handler'] = "'billing'"
        self.assertIn(ErrorCode.Bad_Cell, self._get_codes())

# ################################################################################################################################

    def test_column_assigning_nothing(self) -> 'None':
        """ A column without any action cells is reported.
        """
        column = self.table['columns'][2]
        column['actions'] = {}
        self.assertIn(ErrorCode.Bad_Column, self._get_codes())

# ################################################################################################################################

    def test_bad_statement_severity(self) -> 'None':
        """ A statement severity outside info, warning and violation is reported.
        """
        column = self.table['columns'][1]
        statement = column['statement']
        statement['severity'] = 'fatal'
        self.assertIn(ErrorCode.Bad_Statement, self._get_codes())

# ################################################################################################################################

    def test_bad_filter(self) -> 'None':
        """ A filter with a bad subject or an empty cell is reported.
        """
        self.table['filter'] = {'subject': '9bad', 'cell': ''}
        codes = self._get_codes()
        self.assertIn(ErrorCode.Bad_Row, codes)
        self.assertIn(ErrorCode.Bad_Cell, codes)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
