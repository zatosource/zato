# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rule_engine.table_checks import check_conflicts, check_subsumption, check_unreachable

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

def _new_table(columns:'dictlist') -> 'anydict':
    """ Builds a table with the shared rows and the given rule columns.
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
            {'target': 'rate'},
        ],
        'columns': columns,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCheckConflicts(unittest.TestCase):
    """ Tests conflict detection between overlapping columns with differing actions.
    """

    def test_overlapping_columns_with_different_values_conflict(self) -> 'None':
        """ Two columns one input can satisfy, assigning different values, are one conflict.
        """
        columns = [
            {'number': 1, 'cells': {'a': '>= 700'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': '700..850'}, 'actions': {'approved': 'false'}},
        ]
        result = check_conflicts(_new_table(columns))

        conflicts = result['conflicts']
        self.assertEqual(len(conflicts), 1)

        conflict = conflicts[0]
        self.assertEqual(conflict['first'], 1)
        self.assertEqual(conflict['second'], 2)
        self.assertListEqual(conflict['targets'], ['approved'])

# ################################################################################################################################

    def test_disjoint_columns_never_conflict(self) -> 'None':
        """ Columns no single input can satisfy together never conflict, whatever they assign.
        """
        columns = [
            {'number': 1, 'cells': {'a': '< 500'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': '700..850'}, 'actions': {'approved': 'false'}},
        ]
        result = check_conflicts(_new_table(columns))
        self.assertListEqual(result['conflicts'], [])

# ################################################################################################################################

    def test_agreeing_columns_never_conflict(self) -> 'None':
        """ Overlapping columns that assign the same values do not conflict.
        """
        columns = [
            {'number': 1, 'cells': {'a': '>= 700'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'b': 'Gold'}, 'actions': {'approved': 'true'}},
        ]
        result = check_conflicts(_new_table(columns))
        self.assertListEqual(result['conflicts'], [])

# ################################################################################################################################

    def test_blank_rows_always_overlap(self) -> 'None':
        """ Columns constraining different rows overlap through the blanks, so they can conflict.
        """
        columns = [
            {'number': 1, 'cells': {'a': '>= 700'}, 'actions': {'rate': '2.9'}},
            {'number': 2, 'cells': {'b': 'Gold'}, 'actions': {'rate': '3.9'}},
        ]
        result = check_conflicts(_new_table(columns))

        conflicts = result['conflicts']
        self.assertEqual(len(conflicts), 1)

        conflict = conflicts[0]
        self.assertListEqual(conflict['targets'], ['rate'])

# ################################################################################################################################

    def test_declared_override_resolves_a_conflict(self) -> 'None':
        """ A column declaring it overrides another turns their conflict into a resolution.
        """
        columns = [
            {'number': 1, 'cells': {'a': '>= 700'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': '700..850'}, 'actions': {'approved': 'false'}, 'overrides': [1]},
        ]
        result = check_conflicts(_new_table(columns))

        self.assertListEqual(result['conflicts'], [])

        overridden = result['overridden']
        self.assertEqual(len(overridden), 1)

        entry = overridden[0]
        self.assertEqual(entry['winner'], 2)
        self.assertEqual(entry['loser'], 1)

# ################################################################################################################################

    def test_unknown_override_is_reported(self) -> 'None':
        """ An override naming a column the table does not have is reported.
        """
        columns = [
            {'number': 1, 'cells': {'a': '>= 700'}, 'actions': {'approved': 'true'}, 'overrides': [9]},
        ]
        result = check_conflicts(_new_table(columns))

        unknown = result['unknown_overrides']
        self.assertEqual(len(unknown), 1)

        entry = unknown[0]
        self.assertEqual(entry['column'], 1)
        self.assertEqual(entry['overrides'], 9)

# ################################################################################################################################
# ################################################################################################################################

class TestCheckSubsumption(unittest.TestCase):
    """ Tests that a column covered whole by a more general one is always flagged.
    """

    def test_narrower_range_is_subsumed(self) -> 'None':
        """ A range inside a wider comparison is subsumed by it.
        """
        columns = [
            {'number': 1, 'cells': {'a': '>= 500'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': '700..850'}, 'actions': {'approved': 'true'}},
        ]
        findings = check_subsumption(_new_table(columns))

        self.assertEqual(len(findings), 1)

        finding = findings[0]
        self.assertEqual(finding['general'], 1)
        self.assertEqual(finding['specific'], 2)

# ################################################################################################################################

    def test_blank_cell_subsumes_any_cell(self) -> 'None':
        """ A column leaving a row blank covers any column constraining it.
        """
        columns = [
            {'number': 1, 'cells': {'b': 'Gold'}, 'actions': {'rate': '2.9'}},
            {'number': 2, 'cells': {'a': '>= 700', 'b': 'Gold'}, 'actions': {'rate': '2.9'}},
        ]
        findings = check_subsumption(_new_table(columns))

        self.assertEqual(len(findings), 1)

        finding = findings[0]
        self.assertEqual(finding['general'], 1)
        self.assertEqual(finding['specific'], 2)

# ################################################################################################################################

    def test_membership_subsumes_its_member(self) -> 'None':
        """ A set membership cell covers an equality against one of its members.
        """
        columns = [
            {'number': 1, 'cells': {'b': 'in {Gold, Platinum}'}, 'actions': {'rate': '2.9'}},
            {'number': 2, 'cells': {'b': 'Gold'}, 'actions': {'rate': '2.9'}},
        ]
        findings = check_subsumption(_new_table(columns))

        self.assertEqual(len(findings), 1)

        finding = findings[0]
        self.assertEqual(finding['general'], 1)
        self.assertEqual(finding['specific'], 2)

# ################################################################################################################################

    def test_disjoint_columns_are_not_subsumed(self) -> 'None':
        """ Columns over separate value spaces subsume nothing.
        """
        columns = [
            {'number': 1, 'cells': {'a': '< 500'}, 'actions': {'approved': 'false'}},
            {'number': 2, 'cells': {'a': '700..850'}, 'actions': {'approved': 'true'}},
        ]
        findings = check_subsumption(_new_table(columns))
        self.assertListEqual(findings, [])

# ################################################################################################################################

    def test_equivalent_columns_come_back_once(self) -> 'None':
        """ Two columns with the same conditions come back as one finding, lower number general.
        """
        columns = [
            {'number': 1, 'cells': {'a': '>= 700'}, 'actions': {'approved': 'true'}},
            {'number': 2, 'cells': {'a': '>= 700'}, 'actions': {'approved': 'false'}},
        ]
        findings = check_subsumption(_new_table(columns))

        self.assertEqual(len(findings), 1)

        finding = findings[0]
        self.assertEqual(finding['general'], 1)
        self.assertEqual(finding['specific'], 2)

# ################################################################################################################################
# ################################################################################################################################

class TestCheckUnreachable(unittest.TestCase):
    """ Tests detection of columns whose own conditions contradict each other.
    """

    def test_cell_contradicting_the_filter_is_unreachable(self) -> 'None':
        """ A cell sharing the filter's subject with no common value can never fire.
        """
        columns = [
            {'number': 1, 'cells': {'a': '<= 0'}, 'actions': {'approved': 'false'}},
        ]
        table = _new_table(columns)
        table['conditions'] = [{'letter': 'a', 'subject': 'amount'}]
        table['filter'] = {'subject': 'amount', 'cell': '> 0'}

        findings = check_unreachable(table)
        self.assertEqual(len(findings), 1)

        finding = findings[0]
        self.assertEqual(finding['column'], 1)
        self.assertEqual(finding['subject'], 'amount')

# ################################################################################################################################

    def test_two_rows_on_one_subject_can_contradict(self) -> 'None':
        """ Two condition rows over the same subject with disjoint cells make a column unreachable.
        """
        columns = [
            {'number': 1, 'cells': {'a': '< 500', 'b': '>= 700'}, 'actions': {'approved': 'true'}},
        ]
        table = _new_table(columns)
        table['conditions'] = [
            {'letter': 'a', 'subject': 'credit_score'},
            {'letter': 'b', 'subject': 'credit_score'},
        ]

        findings = check_unreachable(table)
        self.assertEqual(len(findings), 1)

        finding = findings[0]
        self.assertEqual(finding['subject'], 'credit_score')

# ################################################################################################################################

    def test_consistent_columns_are_reachable(self) -> 'None':
        """ A column whose constraints share values raises no finding.
        """
        columns = [
            {'number': 1, 'cells': {'a': '700..850', 'b': 'Gold'}, 'actions': {'approved': 'true'}},
        ]
        table = _new_table(columns)
        table['filter'] = {'subject': 'amount', 'cell': '> 0'}

        findings = check_unreachable(table)
        self.assertListEqual(findings, [])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
