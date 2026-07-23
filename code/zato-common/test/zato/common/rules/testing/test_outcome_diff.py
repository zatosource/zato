# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rules.outcome_diff import ChangeStatus, OutcomeStatus, outcome_diff
from zato.common.rules.parser import parse_data_details

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The version running today - preferential from 700 up, standard below.
_old_text = """
rule
    Preferential_rate
when
    credit_score is at least 700
then
    rate = 2.9
    approved = true

rule
    Standard_rate
when
    credit_score is less than 700
then
    rate = 4.5
    approved = false
"""

# The candidate version - the bar moves to 750 and preferential outcomes gain a tier.
_new_text = """
rule
    Preferential_rate
when
    credit_score is at least 750
then
    rate = 2.9
    approved = true
    tier = 'top'

rule
    Standard_rate
when
    credit_score is less than 750
then
    rate = 4.5
    approved = false
"""

# ################################################################################################################################

def _parse(text:'str') -> 'anydict':
    """ Parses rules text into documents keyed by full name.
    """
    documents, errors = parse_data_details(text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################
# ################################################################################################################################

class TestOutcomeDiff(unittest.TestCase):
    """ Tests replaying scenarios against two rule versions.
    """

    def setUp(self) -> 'None':
        self.old_documents = _parse(_old_text)
        self.new_documents = _parse(_new_text)

# ################################################################################################################################

    def _diff_one(self, name:'str', credit_score:'int') -> 'anydict':
        """ Diffs one scenario between the two shared versions.
        """
        scenarios = [{'name': name, 'input': {'credit_score': credit_score}}]
        result = outcome_diff(self.old_documents, self.new_documents, scenarios)

        out = result['scenarios'][0]
        return out

# ################################################################################################################################

    def test_unchanged_decision(self) -> 'None':
        """ A scenario both versions decide the same way is unchanged, with no changes listed.
        """
        entry = self._diff_one('Low score', 600)

        self.assertEqual(entry['status'], OutcomeStatus.Unchanged)
        self.assertListEqual(entry['changes'], [])
        self.assertListEqual(entry['fired_only_old'], [])
        self.assertListEqual(entry['fired_only_new'], [])

# ################################################################################################################################

    def test_changed_decision_names_fields_and_rules(self) -> 'None':
        """ A decision that flips lists every changed field and the rules that explain it.
        """
        entry = self._diff_one('Mid score', 720)

        self.assertEqual(entry['status'], OutcomeStatus.Changed)

        changes = entry['changes']
        self.assertEqual(len(changes), 2)

        first = changes[0]
        second = changes[1]

        self.assertEqual(first['field'], 'approved')
        self.assertEqual(first['status'], ChangeStatus.Different)
        self.assertEqual(first['old'], True)
        self.assertEqual(first['new'], False)

        self.assertEqual(second['field'], 'rate')
        self.assertEqual(second['old'], 2.9)
        self.assertEqual(second['new'], 4.5)

        # The attribution is the rules that fired in one version only.
        self.assertListEqual(entry['fired_only_old'], ['loans_Preferential_rate'])
        self.assertListEqual(entry['fired_only_new'], ['loans_Standard_rate'])

# ################################################################################################################################

    def test_added_field_is_a_change(self) -> 'None':
        """ A field only the new version assigns comes back as added, even with the same rules firing.
        """
        entry = self._diff_one('High score', 800)

        self.assertEqual(entry['status'], OutcomeStatus.Changed)

        changes = entry['changes']
        self.assertEqual(len(changes), 1)

        change = changes[0]
        self.assertEqual(change['field'], 'tier')
        self.assertEqual(change['status'], ChangeStatus.Added)
        self.assertIsNone(change['old'])
        self.assertEqual(change['new'], 'top')

        # The same rule fired on both sides, so nothing is attributed.
        self.assertListEqual(entry['fired_only_old'], [])
        self.assertListEqual(entry['fired_only_new'], [])

# ################################################################################################################################

    def test_removed_field_is_a_change(self) -> 'None':
        """ A field only the old version assigns comes back as removed.
        """
        scenarios = [{'name': 'High score', 'input': {'credit_score': 800}}]
        result = outcome_diff(self.new_documents, self.old_documents, scenarios)

        entry = result['scenarios'][0]
        changes = entry['changes']

        change = changes[0]
        self.assertEqual(change['field'], 'tier')
        self.assertEqual(change['status'], ChangeStatus.Removed)
        self.assertEqual(change['old'], 'top')
        self.assertIsNone(change['new'])

# ################################################################################################################################

    def test_unevaluable_scenario_never_stops_the_replay(self) -> 'None':
        """ A scenario the rules cannot evaluate is an error entry, the rest still replays.
        """
        scenarios = [
            {'name': 'No score', 'input': {}},
            {'name': 'Low score', 'input': {'credit_score': 600}},
        ]
        result = outcome_diff(self.old_documents, self.new_documents, scenarios)

        self.assertEqual(result['total'], 2)
        self.assertEqual(result['errors'], 1)
        self.assertEqual(result['unchanged'], 1)

        first = result['scenarios'][0]
        self.assertEqual(first['status'], OutcomeStatus.Error)
        self.assertIn("the input has no value for 'credit_score'", first['error'])

# ################################################################################################################################

    def test_totals_add_up(self) -> 'None':
        """ The summary counts cover every scenario of the replay.
        """
        scenarios = [
            {'name': 'High score', 'input': {'credit_score': 800}},
            {'name': 'Mid score', 'input': {'credit_score': 720}},
            {'name': 'Low score', 'input': {'credit_score': 600}},
            {'name': 'No score', 'input': {}},
        ]
        result = outcome_diff(self.old_documents, self.new_documents, scenarios)

        self.assertEqual(result['total'], 4)
        self.assertEqual(result['changed'], 2)
        self.assertEqual(result['unchanged'], 1)
        self.assertEqual(result['errors'], 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
