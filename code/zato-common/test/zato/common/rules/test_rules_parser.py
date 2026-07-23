# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import unittest
from pathlib import Path

# Zato
from zato.common.rules.api import RulesManager
from zato.common.rules.document import Comparator, NodeKind
from zato.common.rules.parser import ErrorCode, parse_data, parse_data_details, parse_file

# ################################################################################################################################
# ################################################################################################################################

class TestRulesParser(unittest.TestCase):

    def test_parse_all_fixture_files(self) -> 'None':
        """ Every fixture file parses into documents that load into a rules manager.
        """

        # Find all the non-performance fixture files ..
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        zrules_dir = current_dir / 'zrules'

        zrules_files = []
        for item in zrules_dir.glob('*.zrules'):
            zrules_files.append(item)

        self.assertTrue(zrules_files, 'No .zrules files found in the zrules subdirectory')

        # .. parse and load each of them ..
        rules_manager = RulesManager()
        loaded_rules = []

        for zrules_file in zrules_files:
            container_name = zrules_file.stem

            documents = parse_file(zrules_file, container_name)
            self.assertTrue(documents, f'No rules parsed from {zrules_file}')

            rule_names = rules_manager.load_parsed_rules(documents, container_name)
            self.assertTrue(rule_names, f'No rules loaded from {zrules_file}')

            loaded_rules.extend(rule_names)

        # .. and confirm each loaded rule is complete.
        for rule_name in loaded_rules:
            rule = rules_manager[rule_name]
            self.assertEqual(rule.full_name, rule_name)
            self.assertTrue(rule.when, f'Rule {rule_name} is missing its when expression')
            self.assertTrue(rule.when_impl is not None, f'Rule {rule_name} is missing when_impl')
            self.assertTrue(rule.document, f'Rule {rule_name} is missing its document')

# ################################################################################################################################

    def test_block_parsing(self) -> 'None':
        """ All the blocks of a rule end up in the document.
        """
        text = """
        rule
            Order_priority
        docs
            Orders above the threshold are handled first.
        defaults
            threshold = 1000
        when
            order.amount is more than default.threshold
        then
            priority = 'high'
        else
            priority = 'standard'
        """
        documents, errors = parse_data_details(text, 'orders')

        self.assertListEqual(errors, [])
        document = documents['orders_Order_priority']

        self.assertEqual(document['name'], 'Order_priority')
        self.assertEqual(document['docs'], 'Orders above the threshold are handled first.')
        self.assertEqual(document['defaults']['threshold'], {'kind': NodeKind.Literal, 'value': 1000})
        self.assertEqual(len(document['conditions']), 1)
        self.assertListEqual(document['joiners'], [])
        self.assertEqual(document['then'], [{'target': 'priority', 'value': {'kind': NodeKind.Literal, 'value': 'high'}}])
        self.assertEqual(document['else'], [{'target': 'priority', 'value': {'kind': NodeKind.Literal, 'value': 'standard'}}])
        self.assertEqual(document['container_name'], 'orders')
        self.assertEqual(document['full_name'], 'orders_Order_priority')

# ################################################################################################################################

    def test_comparator_aliases(self) -> 'None':
        """ Symbol aliases parse into the same canonical comparators as the sentence forms.
        """
        text = """
        rule
            Alias_check
        when
            amount == 100 and
            status != 'closed' and
            score < 10 and
            weight <= 20 and
            height >= 30 and
            depth > 40 and
            category in 'standard', 'expedited' and
            channel not in 'fax', 'pager' and
            doc_id =~ 'AAABBB\\s\\S+'
        then
            result = 'aliases'
        """
        documents, errors = parse_data_details(text, 'demo')

        self.assertListEqual(errors, [])
        conditions = documents['demo_Alias_check']['conditions']

        expected = [
            Comparator.Is,
            Comparator.Is_Not,
            Comparator.Is_Less_Than,
            Comparator.Is_At_Most,
            Comparator.Is_At_Least,
            Comparator.Is_More_Than,
            Comparator.Is_One_Of,
            Comparator.Is_Not_One_Of,
            Comparator.Matches,
        ]

        actual = []
        for condition in conditions:
            actual.append(condition['comparator'])

        self.assertListEqual(actual, expected)

# ################################################################################################################################

    def test_tagged_value_nodes(self) -> 'None':
        """ Values parse into explicitly tagged nodes - literals, lists, objects and references.
        """
        text = """
        rule
            Node_kinds
        when
            abc is 123
        then
            count = 42
            ratio = 0.75
            label = 'approved'
            flag = true
            starts = d'2025-01-01T00:00:00'
            channels = 'sms', channel
            tiers = ['gold', 'platinum']
            status = {'key1': 'value1', 'key2': 'value2'}
            source = customer.segment
        """
        documents, errors = parse_data_details(text, 'demo')

        self.assertListEqual(errors, [])

        actions = {}
        for action in documents['demo_Node_kinds']['then']:
            actions[action['target']] = action['value']

        self.assertEqual(actions['count'], {'kind': NodeKind.Literal, 'value': 42})
        self.assertEqual(actions['ratio'], {'kind': NodeKind.Literal, 'value': 0.75})
        self.assertEqual(actions['label'], {'kind': NodeKind.Literal, 'value': 'approved'})
        self.assertEqual(actions['flag'], {'kind': NodeKind.Literal, 'value': True})
        self.assertEqual(actions['starts'], {'kind': NodeKind.Literal, 'value': '2025-01-01T00:00:00', 'value_type': 'datetime'})

        self.assertEqual(actions['channels']['kind'], NodeKind.List)
        self.assertEqual(actions['channels']['items'][0], {'kind': NodeKind.Literal, 'value': 'sms'})
        self.assertEqual(actions['channels']['items'][1], {'kind': NodeKind.Reference, 'term': 'channel'})

        self.assertEqual(actions['tiers']['kind'], NodeKind.List)
        self.assertEqual(actions['status'], {'kind': NodeKind.Object, 'value': {'key1': 'value1', 'key2': 'value2'}})
        self.assertEqual(actions['source'], {'kind': NodeKind.Reference, 'term': 'customer.segment'})

# ################################################################################################################################

    def test_comment_skipping(self) -> 'None':
        """ Comments are legal anywhere and never survive into the document.
        """
        text = """
        # A leading comment before the rule.
        rule
            Comment_check # The rule name line can carry a comment too.
        when
            amount is more than 100 # Only large amounts qualify.
        then
            note = 'The # inside quotes stays' # But this one goes.
        """
        documents, errors = parse_data_details(text, 'demo')

        self.assertListEqual(errors, [])
        document = documents['demo_Comment_check']

        self.assertEqual(document['name'], 'Comment_check')
        self.assertEqual(document['then'][0]['value'], {'kind': NodeKind.Literal, 'value': 'The # inside quotes stays'})

# ################################################################################################################################

    def test_parenthesis_rejected(self) -> 'None':
        """ A parenthesis in a condition is a structured error telling the author to split the rule.
        """
        text = """
        rule
            Paren_check
        when
            (amount is more than 100 or amount is less than 10) and
            status is 'active'
        then
            result = 'never'
        """
        documents, errors = parse_data_details(text, 'demo')

        self.assertDictEqual(dict(documents), {})
        self.assertEqual(errors[0]['code'], ErrorCode.Parenthesis)
        self.assertEqual(errors[0]['rule'], 'Paren_check')
        self.assertEqual(errors[0]['block'], 'when')
        self.assertIn('two rules', errors[0]['message'])

# ################################################################################################################################

    def test_unknown_comparator(self) -> 'None':
        """ An unknown comparator is a structured error carrying the offending text.
        """
        text = """
        rule
            Comparator_check
        when
            amount exceeds 100
        then
            result = 'never'
        """
        documents, errors = parse_data_details(text, 'demo')

        self.assertDictEqual(dict(documents), {})
        self.assertEqual(errors[0]['code'], ErrorCode.Unknown_Comparator)
        self.assertEqual(errors[0]['field'], 'amount')

# ################################################################################################################################

    def test_wrong_arity(self) -> 'None':
        """ Giving a comparator the wrong number of values is a structured error.
        """
        text = """
        rule
            Arity_check
        when
            enabled is true 'yes' and
            amount is between 100 and
            status is 'active', 'pending'
        then
            result = 'never'
        """
        documents, errors = parse_data_details(text, 'demo')

        self.assertDictEqual(dict(documents), {})

        codes = []
        for error in errors:
            codes.append(error['code'])

        self.assertIn(ErrorCode.Wrong_Arity, codes)

# ################################################################################################################################

    def test_invoke_rejected(self) -> 'None':
        """ The invoke block is rejected with a message pointing to the calling service.
        """
        text = """
        rule
            Invoke_check
        invoke
            result1 = abc.service1(request1)
        when
            abc is 123
        then
            result = 'never'
        """
        documents, errors = parse_data_details(text, 'demo')

        self.assertEqual(errors[0]['code'], ErrorCode.Invoke_Block)
        self.assertIn('calling service', errors[0]['message'])

        # The rest of the rule still parses - the error is precise, not fatal to the file.
        self.assertIn('demo_Invoke_check', documents)

# ################################################################################################################################

    def test_missing_joiner(self) -> 'None':
        """ A condition line without a trailing joiner, other than the last one, is a structured error.
        """
        text = """
        rule
            Joiner_check
        when
            amount is more than 100
            status is 'active'
        then
            result = 'never'
        """
        documents, errors = parse_data_details(text, 'demo')

        self.assertDictEqual(dict(documents), {})
        self.assertEqual(errors[0]['code'], ErrorCode.Missing_Joiner)

# ################################################################################################################################

    def test_defaults_resolution(self) -> 'None':
        """ Defaults resolve to plain values on the loaded rule and references to them compile away.
        """
        text = """
        rule
            Defaults_check
        defaults
            min_score = 740
            tiers = ['gold', 'platinum']
        when
            score is at least default.min_score and
            tier is one of default.tiers
        then
            approved = true
        """
        documents = parse_data(text, 'demo')

        rules_manager = RulesManager()
        _ = rules_manager.load_parsed_rules(documents, 'demo')

        rule = rules_manager['demo_Defaults_check']
        self.assertDictEqual(rule.defaults, {'min_score': 740, 'tiers': ['gold', 'platinum']})
        self.assertEqual(rule.when, 'score >= min_score and tier in tiers')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
