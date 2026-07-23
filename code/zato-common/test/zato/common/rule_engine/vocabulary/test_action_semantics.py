# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rule_engine.errors import Severity
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.semantics import validate_data, validate_document
from zato.common.rule_engine.vocabulary import ErrorCode

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

class TestActionSemantics(unittest.TestCase):
    """ Tests the semantic validation of defaults and then/else actions against a vocabulary.
    """

    def setUp(self) -> 'None':
        self.vocabulary = _get_vocabulary()

# ################################################################################################################################

    def test_unknown_default(self) -> 'None':
        """ A default reference has to point to a default the rule declares.
        """
        document = _parse_one("""
rule
    Missing_default
when
    customer.creditScore is at least default.min_score
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Unknown_Default)

# ################################################################################################################################

    def test_declared_default_is_clean(self) -> 'None':
        """ A default reference pointing to a declared default validates cleanly.
        """
        document = _parse_one("""
rule
    Declared_default
defaults
    min_score = 700
when
    customer.creditScore is at least default.min_score
then
    loan.rate = 2.9
""")
        errors = validate_document(document, self.vocabulary)
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_unknown_default_in_then(self) -> 'None':
        """ A default referenced by an action is checked exactly like one in a condition.
        """
        document = _parse_one("""
rule
    Default_in_then
when
    customer.creditScore is at least 700
then
    loan.rate = default.base_rate
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Unknown_Default)
        self.assertEqual(error['block'], 'then')

# ################################################################################################################################

    def test_then_target_unknown(self) -> 'None':
        """ An action writing to a term the vocabulary does not know is reported.
        """
        document = _parse_one("""
rule
    Unknown_target
when
    customer.creditScore is at least 700
then
    loan.bonus = 100
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Unknown_Term)
        self.assertEqual(error['block'], 'then')
        self.assertEqual(error['field'], 'loan.bonus')

# ################################################################################################################################

    def test_deprecated_target_is_a_warning(self) -> 'None':
        """ An action writing to a deprecated term keeps working but the author is told.
        """
        document = _parse_one("""
rule
    Deprecated_target
when
    customer.creditScore is at least 700
then
    customer.segment = 'Retail'
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Deprecated_Term)
        self.assertEqual(error['severity'], Severity.Warning)
        self.assertEqual(error['block'], 'then')

# ################################################################################################################################

    def test_then_choice_value_checked(self) -> 'None':
        """ A value assigned to a choice term has to be one of its choices, in else as well.
        """
        document = _parse_one("""
rule
    Bad_assignment
when
    customer.creditScore is at least 700
then
    customer.category = 'Diamond'
else
    loan.approved = false
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Choice_Value)
        self.assertEqual(error['block'], 'then')

# ################################################################################################################################

    def test_yes_no_assignment_checked(self) -> 'None':
        """ A text assigned to a yes/no term is reported as a type mismatch.
        """
        document = _parse_one("""
rule
    Text_for_yes_no
when
    customer.creditScore is at least 700
then
    loan.approved = 'yes'
""")
        errors = validate_document(document, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Value_Type)
        self.assertIn('yes/no', error['message'])

# ################################################################################################################################

    def test_each_finding_is_reported(self) -> 'None':
        """ Several problems in one rule are all reported at once.
        """
        document = _parse_one("""
rule
    Many_problems
when
    customer.height is at least 180 and
    customer.category is 'Glod'
then
    loan.bonus = 100
""")
        errors = validate_document(document, self.vocabulary)

        codes = []
        for error in errors:
            codes.append(error['code'])
        codes.sort()

        self.assertListEqual(codes, [ErrorCode.Choice_Value, ErrorCode.Unknown_Term, ErrorCode.Unknown_Term])

# ################################################################################################################################
# ################################################################################################################################

class TestValidateData(unittest.TestCase):
    """ Tests the validation of input data against a vocabulary - the same path the REST boundary shares.
    """

    def setUp(self) -> 'None':
        self.vocabulary = _get_vocabulary()

# ################################################################################################################################

    def test_clean_data(self) -> 'None':
        """ Data with known fields and legal values validates without findings.
        """
        data = {
            'customer.creditScore': 720,
            'customer.category': 'Gold',
            'loan.amount': 250000,
            'loan.approved': False,
        }
        errors = validate_data(data, self.vocabulary)
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_unknown_field(self) -> 'None':
        """ A field the vocabulary does not know is reported by name.
        """
        data = {'customer.height': 180}
        errors = validate_data(data, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Unknown_Field)
        self.assertEqual(error['field'], 'customer.height')

# ################################################################################################################################

    def test_out_of_range_value(self) -> 'None':
        """ A score outside its range is reported in domain terms, never as a bare 400.
        """
        data = {'customer.creditScore': 12000}
        errors = validate_data(data, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Out_Of_Range)
        self.assertIn('12000 is outside 300 to 850', error['message'])

# ################################################################################################################################

    def test_yes_no_field_checked(self) -> 'None':
        """ A text where a yes/no belongs is reported as a type mismatch.
        """
        data = {'loan.approved': 'yes'}
        errors = validate_data(data, self.vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Value_Type)
        self.assertIn('yes/no', error['message'])

# ################################################################################################################################

    def test_wrong_type_and_choice(self) -> 'None':
        """ A text where a number belongs and an unknown choice are both reported.
        """
        data = {
            'loan.amount': 'a lot',
            'customer.category': 'Diamond',
        }
        errors = validate_data(data, self.vocabulary)

        codes = []
        for error in errors:
            codes.append(error['code'])
        codes.sort()

        self.assertListEqual(codes, [ErrorCode.Choice_Value, ErrorCode.Value_Type])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
