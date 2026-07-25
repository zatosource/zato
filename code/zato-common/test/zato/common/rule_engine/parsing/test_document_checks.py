# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from copy import deepcopy

# Zato
from zato.common.rule_engine.document_checks import validate_definition_document, validate_document_shape, \
    validate_documents
from zato.common.rule_engine.parser import parse_data_details

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_rules_text = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
when
    credit_score is at least 700 and
    category is one of [Gold, Platinum]
then
    rate = 2.9
else
    rate = 4.5
"""

# ################################################################################################################################

def _get_document() -> 'anydict':
    """ The one parsed document every test starts from.
    """
    documents, errors = parse_data_details(_rules_text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    out = documents['loans_Preferential_rate']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDocumentShape(unittest.TestCase):
    """ Tests the structural checks over one canonical rule document.
    """

    def setUp(self) -> 'None':
        self.document = _get_document()

# ################################################################################################################################

    def test_a_parsed_document_is_valid(self) -> 'None':
        """ What the parser produces is what the checks accept - they describe the same document.
        """
        errors = validate_document_shape(self.document)
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_a_missing_key_is_named(self) -> 'None':
        """ A document without a key the engine reads is refused, naming the key.
        """
        del self.document['joiners']

        errors = validate_document_shape(self.document)
        self.assertEqual(len(errors), 1)
        self.assertIn('joiners', errors[0]['message'])

# ################################################################################################################################

    def test_a_full_name_of_its_own_is_refused(self) -> 'None':
        """ A full name that is not the ruleset and the rule name together is refused.
        """
        self.document['full_name'] = 'something_else'

        errors = validate_document_shape(self.document)
        self.assertEqual(len(errors), 1)
        self.assertIn('loans_Preferential_rate', errors[0]['message'])

# ################################################################################################################################

    def test_a_comparator_taking_other_values_is_refused(self) -> 'None':
        """ A comparator given more values than it takes is refused, naming the count.
        """
        condition = self.document['conditions'][0]
        condition['values'].append({'kind': 'literal', 'value': 800})

        errors = validate_document_shape(self.document)
        self.assertEqual(len(errors), 1)
        self.assertIn('takes 1 values, not 2', errors[0]['message'])

# ################################################################################################################################

    def test_a_joiner_count_that_cannot_be_right_is_refused(self) -> 'None':
        """ Two conditions take exactly one joiner between them.
        """
        self.document['joiners'] = []

        errors = validate_document_shape(self.document)
        self.assertEqual(len(errors), 1)
        self.assertIn('2 conditions take 1 joiners', errors[0]['message'])

# ################################################################################################################################

    def test_an_untagged_value_is_refused(self) -> 'None':
        """ A plain value where a tagged node belongs is refused - the engine reads nodes, not values.
        """
        self.document['then'][0]['value'] = 2.9

        errors = validate_document_shape(self.document)
        self.assertEqual(len(errors), 1)
        self.assertIn('tagged node', errors[0]['message'])

# ################################################################################################################################

    def test_a_rule_assigning_nothing_is_refused(self) -> 'None':
        """ A rule with no then action decides nothing when it fires.
        """
        self.document['then'] = []

        errors = validate_document_shape(self.document)
        self.assertEqual(len(errors), 1)
        self.assertIn('at least one then action', errors[0]['message'])

# ################################################################################################################################

    def test_an_expression_that_does_not_compile_is_refused(self) -> 'None':
        """ A shape the checks accept but the engine's own grammar does not is still refused.
        """
        self.document['conditions'][0]['subject'] = 'true'
        self.document['conditions'][0]['comparator'] = 'matches'

        errors = validate_document_shape(self.document)
        self.assertEqual(len(errors), 1)
        self.assertIn('does not compile', errors[0]['message'])

# ################################################################################################################################
# ################################################################################################################################

class TestRulesetDocuments(unittest.TestCase):
    """ Tests the checks over the whole set of documents one stored ruleset carries.
    """

    def setUp(self) -> 'None':
        self.document = _get_document()
        self.documents = {self.document['full_name']: self.document}

# ################################################################################################################################

    def test_a_parsed_ruleset_is_valid(self) -> 'None':
        """ A ruleset of parsed documents passes as it stands.
        """
        errors = validate_documents(self.documents)
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_an_empty_ruleset_is_refused(self) -> 'None':
        """ A ruleset with no rules decides nothing and is refused rather than stored.
        """
        errors = validate_documents({})
        self.assertEqual(len(errors), 1)
        self.assertIn('at least one rule', errors[0]['message'])

# ################################################################################################################################

    def test_a_key_that_is_not_the_full_name_is_refused(self) -> 'None':
        """ A document has to be stored under the name everything else refers to it by.
        """
        documents = {'loans_Other_name': self.document}

        errors = validate_documents(documents)
        self.assertEqual(len(errors), 1)
        self.assertIn('calls itself', errors[0]['message'])

# ################################################################################################################################

    def test_rules_of_two_rulesets_in_one_snapshot_are_refused(self) -> 'None':
        """ One stored snapshot holds the rules of one ruleset, because that is the name it loads under.
        """
        other = deepcopy(self.document)
        other['ruleset_name'] = 'mortgages'
        other['full_name'] = 'mortgages_Preferential_rate'

        documents = dict(self.documents)
        documents[other['full_name']] = other

        errors = validate_documents(documents)
        self.assertEqual(len(errors), 1)
        self.assertIn('belongs to mortgages', errors[0]['message'])

# ################################################################################################################################
# ################################################################################################################################

class TestDefinitionDocuments(unittest.TestCase):
    """ Tests that every definition type carries checks of its own.
    """

    def test_every_type_is_validated(self) -> 'None':
        """ No type reaches the store on a browser's word - each one refuses an empty document.
        """
        for object_type in ('ruleset', 'sentence-rule', 'decision-table', 'vocabulary', 'test-set'):
            errors = validate_definition_document(object_type, {})
            self.assertTrue(errors, object_type)

# ################################################################################################################################

    def test_an_unknown_type_is_refused(self) -> 'None':
        """ A type the store does not have is refused rather than waved through unvalidated.
        """
        errors = validate_definition_document('bicycle', {})
        self.assertEqual(len(errors), 1)
        self.assertIn('Unknown rule definition type', errors[0]['message'])

# ################################################################################################################################

    def test_a_document_of_another_shape_is_reported(self) -> 'None':
        """ A document its own validation cannot read comes back as a finding, not as an exception.
        """
        table = {'name': 'Loans', 'conditions': ['not a row'], 'actions': [], 'columns': []}

        errors = validate_definition_document('decision-table', table)
        self.assertEqual(len(errors), 1)
        self.assertIn('cannot be read as a decision-table', errors[0]['message'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
