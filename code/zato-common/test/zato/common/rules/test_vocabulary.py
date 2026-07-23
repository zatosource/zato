# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from copy import deepcopy

# Zato
from zato.common.rules.parser import parse_data_details
from zato.common.rules.vocabulary import ErrorCode, Severity, default_phrase, default_set_phrase, get_attribute, \
    picker_paths, term_words, validate_data, validate_document, validate_vocabulary

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

class TestPhrases(unittest.TestCase):
    """ Tests the derivation of default phrases from term names.
    """

    def test_term_words(self) -> 'None':
        """ Camel case and underscores both split into lowercase words.
        """
        self.assertEqual(term_words('creditScore'), 'credit score')
        self.assertEqual(term_words('years_as_customer'), 'years as customer')
        self.assertEqual(term_words('amount'), 'amount')

# ################################################################################################################################

    def test_default_phrase(self) -> 'None':
        """ A sensible readable phrase exists by default, derived from the term name.
        """
        self.assertEqual(default_phrase('loan', 'amount'), 'the loan amount')
        self.assertEqual(default_phrase('customer', 'creditScore'), 'the customer credit score')

# ################################################################################################################################

    def test_default_set_phrase(self) -> 'None':
        """ The action phrase wraps the default phrase.
        """
        self.assertEqual(default_set_phrase('loan', 'rate'), 'set the loan rate to')

# ################################################################################################################################
# ################################################################################################################################

class TestLookups(unittest.TestCase):
    """ Tests attribute lookup and picker behavior.
    """

    def test_get_attribute(self) -> 'None':
        """ A term is found by its dotted path and an unknown path returns None.
        """
        vocabulary = _get_vocabulary()

        attribute = get_attribute(vocabulary, 'customer.creditScore')
        self.assertIsNotNone(attribute)

        if attribute:
            self.assertEqual(attribute['type'], 'number range')

        self.assertIsNone(get_attribute(vocabulary, 'customer.height'))

# ################################################################################################################################

    def test_picker_paths_exclude_deprecated(self) -> 'None':
        """ Deprecated terms keep old rules running but never appear in a picker again.
        """
        vocabulary = _get_vocabulary()
        paths = picker_paths(vocabulary)

        self.assertIn('customer.creditScore', paths)
        self.assertNotIn('customer.segment', paths)

# ################################################################################################################################
# ################################################################################################################################

class TestValidateVocabulary(unittest.TestCase):
    """ Tests the structural validation of a vocabulary document itself.
    """

    def test_clean_vocabulary(self) -> 'None':
        """ The reference vocabulary validates without findings.
        """
        errors = validate_vocabulary(_get_vocabulary())
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_duplicate_phrase(self) -> 'None':
        """ Two terms wearing the same phrase are reported - the ambiguity that makes rules unreadable.
        """
        vocabulary = deepcopy(_get_vocabulary())
        loan = vocabulary['entities'][1]
        amount = loan['attributes'][0]
        amount['phrase'] = "the customer's credit score"

        errors = validate_vocabulary(vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Duplicate_Phrase)
        self.assertIn('customer.creditScore', error['message'])
        self.assertIn('loan.amount', error['message'])

# ################################################################################################################################

    def test_unknown_type(self) -> 'None':
        """ A type outside the term types is reported along with the legal list.
        """
        vocabulary = deepcopy(_get_vocabulary())
        loan = vocabulary['entities'][1]
        amount = loan['attributes'][0]
        amount['type'] = 'decimal'

        errors = validate_vocabulary(vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Unknown_Type)
        self.assertIn('decimal', error['message'])
        self.assertIn('number range', error['message'])

# ################################################################################################################################

    def test_choice_without_values(self) -> 'None':
        """ A choice with nothing to choose from is reported.
        """
        vocabulary = deepcopy(_get_vocabulary())
        customer = vocabulary['entities'][0]
        category = customer['attributes'][1]
        category['values'] = []

        errors = validate_vocabulary(vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Missing_Values)

# ################################################################################################################################

    def test_bad_domain(self) -> 'None':
        """ A range whose low does not sit below its high is reported.
        """
        vocabulary = deepcopy(_get_vocabulary())
        customer = vocabulary['entities'][0]
        credit_score = customer['attributes'][0]
        credit_score['domain'] = {'low': 850, 'high': 300}

        errors = validate_vocabulary(vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Bad_Domain)

# ################################################################################################################################

    def test_duplicate_attribute(self) -> 'None':
        """ The same attribute defined twice within one entity is reported.
        """
        vocabulary = deepcopy(_get_vocabulary())
        customer = vocabulary['entities'][0]
        attributes = customer['attributes']
        duplicate = deepcopy(attributes[0])
        duplicate['phrase'] = 'another phrase entirely'
        attributes.append(duplicate)

        errors = validate_vocabulary(vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Duplicate_Attribute)

# ################################################################################################################################
# ################################################################################################################################

class TestValidateDocument(unittest.TestCase):
    """ Tests the semantic validation of rule documents against a vocabulary.
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
