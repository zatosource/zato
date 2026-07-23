# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from copy import deepcopy

# Zato
from zato.common.rules.vocabulary import ErrorCode, default_phrase, default_set_phrase, get_attribute, picker_paths, \
    term_words, validate_vocabulary

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

    def test_bad_entity_name(self) -> 'None':
        """ An entity whose name is not an identifier is reported.
        """
        vocabulary = deepcopy(_get_vocabulary())
        customer = vocabulary['entities'][0]
        customer['name'] = 'customer info'

        errors = validate_vocabulary(vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Bad_Name)
        self.assertIn('customer info', error['message'])

# ################################################################################################################################

    def test_bad_attribute_name(self) -> 'None':
        """ An attribute whose name is not an identifier is reported under its full path.
        """
        vocabulary = deepcopy(_get_vocabulary())
        customer = vocabulary['entities'][0]
        credit_score = customer['attributes'][0]
        credit_score['name'] = 'credit score'

        errors = validate_vocabulary(vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Bad_Name)
        self.assertEqual(error['field'], 'customer.credit score')

# ################################################################################################################################

    def test_duplicate_entity(self) -> 'None':
        """ The same entity defined twice is reported, with its phrases made distinct to isolate the finding.
        """
        vocabulary = deepcopy(_get_vocabulary())
        customer = vocabulary['entities'][0]
        duplicate = deepcopy(customer)

        for attribute in duplicate['attributes']:
            attribute['phrase'] = attribute['phrase'] + ' again'

        vocabulary['entities'].append(duplicate)

        errors = validate_vocabulary(vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Duplicate_Entity)
        self.assertEqual(error['field'], 'customer')

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

    def test_incomplete_domain(self) -> 'None':
        """ A range whose domain misses one of its bounds is reported.
        """
        vocabulary = deepcopy(_get_vocabulary())
        customer = vocabulary['entities'][0]
        credit_score = customer['attributes'][0]
        credit_score['domain'] = {'low': 300}

        errors = validate_vocabulary(vocabulary)
        self.assertEqual(len(errors), 1)

        error = errors[0]
        self.assertEqual(error['code'], ErrorCode.Bad_Domain)
        self.assertIn('needs a domain with low and high', error['message'])

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

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
