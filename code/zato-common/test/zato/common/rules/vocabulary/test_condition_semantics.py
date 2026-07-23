# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rules.errors import Severity
from zato.common.rules.parser import parse_data_details
from zato.common.rules.semantics import validate_document
from zato.common.rules.vocabulary import ErrorCode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

def _get_vocabulary() -> 'anydict':
    """ A small loan-approval vocabulary covering every term type, including one deprecated term.
    """
    out = {
        'name': 'Loan approval',
        'entities': [
            {'name': 'customer', 'attributes': [
                {'name': 'creditScore', 'type': 'number range', 'domain': {'low': 300, 'high': 850},
                 'phrase': "the customer's credit score", 'status': ''},
                {'name': 'category', 'type': 'choice', 'values': ['Gold', 'Silver', 'Platinum', 'Standard'],
                 'phrase': "the customer's category", 'status': ''},
                {'name': 'name', 'type': 'text', 'phrase': "the customer's name", 'status': ''},
                {'name': 'segment', 'type': 'choice', 'values': ['Retail', 'Private'],
                 'phrase': "the customer's segment", 'status': 'deprecated'},
            ]},
            {'name': 'loan', 'attributes': [
                {'name': 'amount', 'type': 'number', 'phrase': 'the loan amount', 'status': ''},
                {'name': 'approved', 'type': 'yes/no', 'phrase': 'the loan is approved', 'status': ''},
                {'name': 'rate', 'type': 'number', 'phrase': 'the interest rate', 'status': ''},
                {'name': 'purpose', 'type': 'text', 'phrase': 'the loan purpose', 'status': ''},
            ]},
        ],
    }
    return out

# ################################################################################################################################

def _parse_one(text:'str') -> 'anydict':
    """ Parses one rule out of the given text and asserts the parse itself was clean.
    """
    documents, errors = parse_data_details(text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    documents = list(documents.values())

    out = documents[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestConditionSemantics(unittest.TestCase):
    """ Tests the semantic validation of the when side of rule documents against a vocabulary.
    """

    def setUp(self) -> 'None':
        self.vocabulary = _get_vocabulary()

# ################################################################################################################################

    def test_clean_document(self) -> 'None':
        """ A rule using known terms with legal comparators and values validates without findings.
        """
        document = _parse_one("""
rule
    Preferential_rate
when
    customer.creditScore is at least 700 and
    customer.category is one of 'Gold', 'Platinum' and
    loan.approved is true
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_comparator_alias_is_canonical(self) -> 'None':
        """ A symbol alias validates exactly like its canonical comparator.
        """
        document = _parse_one("""
rule
    Alias_rule
when
    customer.creditScore >= 700
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_unknown_term(self) -> 'None':
        """ A term the vocabulary does not know is reported by name.
        """
        document = _parse_one("""
rule
    Unknown_term_rule
when
    customer.height is at least 180
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Unknown_Term)
        self.assertEqual(error['field'], 'customer.height')
        self.assertIn('is not a term of this vocabulary', error['message'])

# ################################################################################################################################

    def test_deprecated_term_is_a_warning(self) -> 'None':
        """ A deprecated term keeps the rule running but the author is told.
        """
        document = _parse_one("""
rule
    Deprecated_rule
when
    customer.segment is 'Retail'
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Deprecated_Term)
        self.assertEqual(error['severity'], Severity.Warning)

# ################################################################################################################################

    def test_comparator_type_mismatch(self) -> 'None':
        """ A comparator that makes no sense for the term's type is reported.
        """
        document = _parse_one("""
rule
    Regex_on_number
when
    customer.creditScore matches 'abc'
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Comparator_Type)
        self.assertIn('number range', error['message'])

# ################################################################################################################################

    def test_boolean_comparator_on_number(self) -> 'None':
        """ Is true cannot be asked of a number.
        """
        document = _parse_one("""
rule
    Is_true_on_number
when
    loan.amount is true
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Comparator_Type)

# ################################################################################################################################

    def test_choice_value_unknown(self) -> 'None':
        """ A value outside a choice's list is reported along with the legal choices.
        """
        document = _parse_one("""
rule
    Misspelled_choice
when
    customer.category is 'Glod'
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Choice_Value)
        self.assertIn('Glod', error['message'])
        self.assertIn('Gold, Silver, Platinum, Standard', error['message'])

# ################################################################################################################################

    def test_choice_values_in_membership(self) -> 'None':
        """ Every value of a membership list is checked against the choice's list.
        """
        document = _parse_one("""
rule
    Membership_choice
when
    customer.category is one of 'Gold', 'Diamond'
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Choice_Value)
        self.assertIn('Diamond', error['message'])

# ################################################################################################################################

    def test_out_of_range(self) -> 'None':
        """ A value outside a range's domain is reported in domain terms.
        """
        document = _parse_one("""
rule
    Score_too_high
when
    customer.creditScore is at least 12000
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Out_Of_Range)
        self.assertIn('12000 is outside 300 to 850', error['message'])

# ################################################################################################################################

    def test_between_bounds_checked(self) -> 'None':
        """ Both boundaries of a between condition are checked against the range's domain.
        """
        document = _parse_one("""
rule
    Between_out_of_domain
when
    customer.creditScore is between 100 and 900
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 2)

        messages = []
        for error in errors:
            self.assertEqual(error['code'], ErrorCode.Out_Of_Range)
            messages.append(error['message'])

        self.assertIn('customer.creditScore value 100 is outside 300 to 850', messages)
        self.assertIn('customer.creditScore value 900 is outside 300 to 850', messages)

# ################################################################################################################################

    def test_value_type_mismatch(self) -> 'None':
        """ A text value compared with a number term is reported.
        """
        document = _parse_one("""
rule
    Text_for_number
when
    loan.amount is 'a lot'
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Value_Type)

# ################################################################################################################################

    def test_datetime_literal_is_reported(self) -> 'None':
        """ A datetime value compared with a number term is reported as a type mismatch.
        """
        document = _parse_one("""
rule
    Datetime_for_number
when
    loan.amount is d'2025-01-15 10:00:00'
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Value_Type)
        self.assertIn('datetime', error['message'])

# ################################################################################################################################

    def test_reference_type_mismatch(self) -> 'None':
        """ A number term cannot be compared with a text term.
        """
        document = _parse_one("""
rule
    Number_versus_text
when
    loan.amount is customer.name
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Reference_Type)
        self.assertIn('loan.amount', error['message'])
        self.assertIn('customer.name', error['message'])

# ################################################################################################################################

    def test_field_to_field_same_group_is_clean(self) -> 'None':
        """ Two number terms compare cleanly, even when one is a plain number and the other a range.
        """
        document = _parse_one("""
rule
    Number_versus_number
when
    loan.amount is less than customer.creditScore
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_reference_in_membership_type_checked(self) -> 'None':
        """ A membership against a term of another type group is reported.
        """
        document = _parse_one("""
rule
    Membership_reference
when
    loan.amount is one of customer.name
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Reference_Type)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
