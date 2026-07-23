# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rule_engine.bootstrap import infer_from_document, vocabulary_from_payload
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.vocabulary import TermType, validate_vocabulary

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
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

def _get_vocabulary() -> 'anydict':
    """ A vocabulary with a couple of known terms, so inference can tell known and unknown apart.
    """
    out = {
        'name': 'Loan approval',
        'entities': [
            {'name': 'customer', 'attributes': [
                {'name': 'creditScore', 'type': 'number range', 'domain': {'low': 300, 'high': 850},
                 'phrase': "the customer's credit score", 'status': ''},
            ]},
        ],
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestVocabularyFromPayload(unittest.TestCase):
    """ Tests the paste-a-payload bootstrap - one JSON example becomes terms, types and a scenario.
    """

    def test_entities_and_types(self) -> 'None':
        """ Top-level mappings become entities and their scalar members become typed attributes.
        """
        payload = {
            'customer': {'creditScore': 720, 'name': 'Jane Doe', 'active': True},
            'loan': {'amount': 250000.0},
        }
        result = vocabulary_from_payload(payload)

        entities = result['entities']
        self.assertEqual(len(entities), 2)

        customer = entities[0]
        self.assertEqual(customer['name'], 'customer')

        attributes = {}
        for attribute in customer['attributes']:
            attributes[attribute['name']] = attribute['type']

        expected = {'creditScore': TermType.Number, 'name': TermType.Text, 'active': TermType.Yes_No}
        self.assertDictEqual(attributes, expected)

        loan = entities[1]
        loan_attribute = loan['attributes'][0]
        self.assertEqual(loan_attribute['type'], TermType.Number)

# ################################################################################################################################

    def test_phrases_are_derived(self) -> 'None':
        """ Every attribute carries a readable phrase derived from its name.
        """
        payload = {'customer': {'creditScore': 720}}
        result = vocabulary_from_payload(payload)

        entity = result['entities'][0]
        attribute = entity['attributes'][0]
        self.assertEqual(attribute['phrase'], 'the customer credit score')

# ################################################################################################################################

    def test_top_level_scalars_join_the_default_entity(self) -> 'None':
        """ A scalar without an entity of its own lands in the default input entity.
        """
        payload = {'channel': 'web', 'customer': {'creditScore': 720}}
        result = vocabulary_from_payload(payload)

        entities = result['entities']
        first_entity = entities[0]
        first_attribute = first_entity['attributes'][0]

        self.assertEqual(first_entity['name'], 'input')
        self.assertEqual(first_attribute['name'], 'channel')
        self.assertEqual(first_attribute['type'], TermType.Text)

# ################################################################################################################################

    def test_nested_mappings_flatten(self) -> 'None':
        """ Mappings nested below an entity flatten into dotted attribute names with readable phrases.
        """
        payload = {'customer': {'address': {'city': 'Prague'}}}
        result = vocabulary_from_payload(payload)

        entity = result['entities'][0]
        attribute = entity['attributes'][0]

        self.assertEqual(attribute['name'], 'address.city')
        self.assertEqual(attribute['type'], TermType.Text)
        self.assertEqual(attribute['phrase'], 'the customer address city')

# ################################################################################################################################

    def test_scenario_replays_the_payload(self) -> 'None':
        """ The first scenario's input holds every value under its vocabulary path.
        """
        payload = {
            'channel': 'web',
            'customer': {'creditScore': 720, 'address': {'city': 'Prague'}},
        }
        result = vocabulary_from_payload(payload)
        scenario = result['scenario']

        self.assertEqual(scenario['name'], 'First scenario')

        expected = {
            'input.channel': 'web',
            'customer.creditScore': 720,
            'customer.address.city': 'Prague',
        }
        self.assertDictEqual(scenario['input'], expected)

# ################################################################################################################################

    def test_generated_vocabulary_validates(self) -> 'None':
        """ The derived vocabulary passes the structural validator without findings.
        """
        payload = {
            'customer': {'creditScore': 720, 'name': 'Jane Doe', 'active': True},
            'loan': {'amount': 250000.0, 'approved': False},
        }
        result = vocabulary_from_payload(payload)

        vocabulary = {'name': 'Bootstrapped', 'entities': result['entities']}
        errors = validate_vocabulary(vocabulary)
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_derivation_is_deterministic(self) -> 'None':
        """ The same payload always produces the same vocabulary.
        """
        payload = {'customer': {'creditScore': 720, 'active': True}}

        first = vocabulary_from_payload(payload)
        second = vocabulary_from_payload(payload)
        self.assertDictEqual(first, second)

# ################################################################################################################################
# ################################################################################################################################

class TestInferFromDocument(unittest.TestCase):
    """ Tests the infer-from-typing bootstrap - unknown terms become proposals typed by their usage.
    """

    def setUp(self) -> 'None':
        self.vocabulary = _get_vocabulary()

# ################################################################################################################################

    def _proposals_by_path(self, text:'str') -> 'anydict':
        """ Parses a rule, runs inference and indexes the proposals by their path.
        """
        document = _parse_one(text)
        proposals = infer_from_document(document, self.vocabulary)

        out = {}
        for proposal in proposals:
            out[proposal['path']] = proposal

        return out

# ################################################################################################################################

    def test_comparator_implies_the_type(self) -> 'None':
        """ Numeric, regex and boolean comparators each imply their subject's type.
        """
        proposals = self._proposals_by_path("""
rule
    Inference_rule
when
    loan.amount is at least 1000 and
    loan.purpose matches 'renovation.*' and
    loan.approved is true
then
    loan.rate = 2.9
""")
        amount = proposals['loan.amount']
        purpose = proposals['loan.purpose']
        approved = proposals['loan.approved']

        self.assertEqual(amount['type'], TermType.Number)
        self.assertEqual(purpose['type'], TermType.Text)
        self.assertEqual(approved['type'], TermType.Yes_No)

# ################################################################################################################################

    def test_literal_value_implies_the_type(self) -> 'None':
        """ With a neutral comparator, the compared literal implies the type.
        """
        proposals = self._proposals_by_path("""
rule
    Literal_rule
when
    loan.amount is 250000 and
    customer.category is 'Gold'
then
    loan.rate = 2.9
""")
        amount = proposals['loan.amount']
        category = proposals['customer.category']

        self.assertEqual(amount['type'], TermType.Number)
        self.assertEqual(category['type'], TermType.Text)

# ################################################################################################################################

    def test_target_takes_the_assigned_type(self) -> 'None':
        """ An action target is typed by the value assigned to it.
        """
        proposals = self._proposals_by_path("""
rule
    Target_rule
when
    customer.creditScore is at least 700
then
    loan.rate = 2.9
    loan.approved = true
""")
        rate = proposals['loan.rate']
        approved = proposals['loan.approved']

        self.assertEqual(rate['type'], TermType.Number)
        self.assertEqual(approved['type'], TermType.Yes_No)

# ################################################################################################################################

    def test_reference_mirrors_the_subject(self) -> 'None':
        """ A term compared against a known subject takes the subject's own type.
        """
        proposals = self._proposals_by_path("""
rule
    Mirror_rule
when
    customer.creditScore is at least customer.minimumScore
then
    loan.rate = 2.9
""")
        minimum_score = proposals['customer.minimumScore']
        self.assertEqual(minimum_score['type'], TermType.Number_Range)

# ################################################################################################################################

    def test_known_terms_are_not_proposed(self) -> 'None':
        """ A term the vocabulary already knows yields no proposal.
        """
        proposals = self._proposals_by_path("""
rule
    Known_rule
when
    customer.creditScore is at least 700
then
    loan.rate = 2.9
""")
        self.assertNotIn('customer.creditScore', proposals)
        self.assertIn('loan.rate', proposals)

# ################################################################################################################################

    def test_first_inference_wins(self) -> 'None':
        """ A term used twice keeps the type its first usage implied.
        """
        proposals = self._proposals_by_path("""
rule
    Repeated_rule
when
    loan.amount is at least 1000 and
    loan.amount is 'unusual'
then
    loan.rate = 2.9
""")
        amount = proposals['loan.amount']
        self.assertEqual(amount['type'], TermType.Number)

# ################################################################################################################################

    def test_proposals_carry_entity_name_and_phrase(self) -> 'None':
        """ Every proposal names its entity, attribute and a derived readable phrase.
        """
        proposals = self._proposals_by_path("""
rule
    Phrase_rule
when
    loan.amount is at least 1000
then
    loan.rate = 2.9
""")
        amount = proposals['loan.amount']

        self.assertEqual(amount['entity'], 'loan')
        self.assertEqual(amount['name'], 'amount')
        self.assertEqual(amount['phrase'], 'the loan amount')
        self.assertEqual(amount['status'], '')

# ################################################################################################################################

    def test_bare_term_joins_the_default_entity(self) -> 'None':
        """ A term without a dotted path is proposed under the default input entity.
        """
        proposals = self._proposals_by_path("""
rule
    Bare_rule
when
    credit_score is at least 700
then
    loan.rate = 2.9
""")
        credit_score = proposals['credit_score']

        self.assertEqual(credit_score['entity'], 'input')
        self.assertEqual(credit_score['name'], 'credit_score')
        self.assertEqual(credit_score['phrase'], 'the input credit score')

# ################################################################################################################################

    def test_membership_list_implies_the_type(self) -> 'None':
        """ A membership condition types its subject from the first literal in the list.
        """
        proposals = self._proposals_by_path("""
rule
    Membership_rule
when
    customer.category is one of 'Gold', 'Platinum'
then
    loan.rate = 2.9
""")
        category = proposals['customer.category']
        self.assertEqual(category['type'], TermType.Text)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
