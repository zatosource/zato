# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.simulation import KpiKind, champion_challenger, simulate, validate_kpis
from zato.common.rule_engine.vocabulary import ErrorCode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# The version running today - preferential from 700 up, standard below.
_champion_text = """
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

# The candidate version - the bar moves to 750.
_challenger_text = """
rule
    Preferential_rate
when
    credit_score is at least 750
then
    rate = 2.9
    approved = true

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

def _get_scenarios() -> 'dictlist':
    """ Three inputs across the interesting score bands.
    """
    out = [
        {'name': 'High score', 'input': {'credit_score': 800}},
        {'name': 'Mid score', 'input': {'credit_score': 720}},
        {'name': 'Low score', 'input': {'credit_score': 600}},
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestValidateKpis(unittest.TestCase):
    """ Tests the structural checks over KPI definitions.
    """

    def test_valid_kpis_have_no_findings(self) -> 'None':
        """ Every kind with its required keys validates cleanly.
        """
        kpis = [
            {'name': 'Approved count', 'kind': KpiKind.Count, 'field': 'approved', 'value': True},
            {'name': 'Approval rate', 'kind': KpiKind.Rate, 'field': 'approved', 'value': True},
            {'name': 'Total rate', 'kind': KpiKind.Sum, 'field': 'rate'},
            {'name': 'Average rate', 'kind': KpiKind.Average, 'field': 'rate'},
            {'name': 'By approval', 'kind': KpiKind.Breakdown, 'field': 'approved'},
        ]
        errors = validate_kpis(kpis)
        self.assertListEqual(errors, [])

# ################################################################################################################################

    def test_bad_definitions_are_reported(self) -> 'None':
        """ A missing name, an unknown kind, a missing field and a count without a value are all findings.
        """
        kpis = [
            {'name': '', 'kind': KpiKind.Count, 'field': 'approved', 'value': True},
            {'name': 'Odd', 'kind': 'median', 'field': 'rate'},
            {'name': 'No field', 'kind': KpiKind.Sum, 'field': ''},
            {'name': 'No value', 'kind': KpiKind.Rate, 'field': 'approved'},
        ]
        errors = validate_kpis(kpis)
        self.assertEqual(len(errors), 4)

        for error in errors:
            self.assertEqual(error['code'], ErrorCode.Bad_Kpi)

        fields = []
        for error in errors:
            fields.append(error['field'])

        self.assertListEqual(fields, ['name', 'kind', 'field', 'value'])

# ################################################################################################################################
# ################################################################################################################################

class TestSimulate(unittest.TestCase):
    """ Tests the batch loop and its incrementally computed KPIs.
    """

    def setUp(self) -> 'None':
        self.documents = _parse(_champion_text)
        self.scenarios = _get_scenarios()

# ################################################################################################################################

    def _get_kpi(self, run:'anydict', name:'str') -> 'anydict':
        """ Finds one KPI result by name, failing loudly when it is not there.
        """
        for kpi in run['kpis']:
            if kpi['name'] == name:
                return kpi

        raise Exception(f'No such KPI -> `{name}`')

# ################################################################################################################################

    def test_counts_rates_sums_and_averages(self) -> 'None':
        """ Every KPI kind aggregates the outcomes the way its name says.
        """
        kpis = [
            {'name': 'Approved count', 'kind': KpiKind.Count, 'field': 'approved', 'value': True},
            {'name': 'Approval rate', 'kind': KpiKind.Rate, 'field': 'approved', 'value': True},
            {'name': 'Total rate', 'kind': KpiKind.Sum, 'field': 'rate'},
            {'name': 'Average rate', 'kind': KpiKind.Average, 'field': 'rate'},
        ]
        run = simulate(self.documents, self.scenarios, kpis)

        self.assertEqual(run['total'], 3)
        self.assertEqual(run['evaluated'], 3)
        self.assertEqual(run['errors'], 0)

        count = self._get_kpi(run, 'Approved count')
        self.assertEqual(count['value'], 2)

        rate = self._get_kpi(run, 'Approval rate')
        self.assertAlmostEqual(rate['value'], 2 / 3)

        total = self._get_kpi(run, 'Total rate')
        self.assertAlmostEqual(total['value'], 2.9 + 2.9 + 4.5)

        average = self._get_kpi(run, 'Average rate')
        self.assertAlmostEqual(average['value'], (2.9 + 2.9 + 4.5) / 3)

# ################################################################################################################################

    def test_breakdown_buckets_by_value(self) -> 'None':
        """ A breakdown KPI counts the outcomes per value of its field.
        """
        kpis = [
            {'name': 'By approval', 'kind': KpiKind.Breakdown, 'field': 'approved'},
        ]
        run = simulate(self.documents, self.scenarios, kpis)

        breakdown = self._get_kpi(run, 'By approval')
        self.assertDictEqual(breakdown['value'], {True: 2, False: 1})

# ################################################################################################################################

    def test_never_assigned_fields_aggregate_to_nothing(self) -> 'None':
        """ A KPI over a field no outcome assigns counts nothing and averages to zero.
        """
        kpis = [
            {'name': 'Tier count', 'kind': KpiKind.Count, 'field': 'tier', 'value': 'top'},
            {'name': 'Average tier', 'kind': KpiKind.Average, 'field': 'tier'},
        ]
        run = simulate(self.documents, self.scenarios, kpis)

        count = self._get_kpi(run, 'Tier count')
        self.assertEqual(count['value'], 0)

        average = self._get_kpi(run, 'Average tier')
        self.assertEqual(average['value'], 0.0)

# ################################################################################################################################

    def test_errors_are_skipped_not_fatal(self) -> 'None':
        """ A scenario the rules cannot evaluate is reported and excluded from every KPI.
        """
        scenarios = list(self.scenarios)
        scenarios.append({'name': 'No score', 'input': {}})

        kpis = [
            {'name': 'Approval rate', 'kind': KpiKind.Rate, 'field': 'approved', 'value': True},
        ]
        run = simulate(self.documents, scenarios, kpis)

        self.assertEqual(run['total'], 4)
        self.assertEqual(run['evaluated'], 3)
        self.assertEqual(run['errors'], 1)

        # The rate divides by what evaluated, not by what was submitted.
        rate = self._get_kpi(run, 'Approval rate')
        self.assertAlmostEqual(rate['value'], 2 / 3)

        last = run['scenarios'][3]
        self.assertIn("the input has no value for 'credit_score'", last['error'])

# ################################################################################################################################

    def test_scenario_results_carry_outcome_and_fired_rules(self) -> 'None':
        """ Each scenario of the batch reports its outcome and the rules that produced it.
        """
        run = simulate(self.documents, self.scenarios, [])

        first = run['scenarios'][0]
        self.assertEqual(first['scenario'], 'High score')
        self.assertEqual(first['outcome']['rate'], 2.9)
        self.assertListEqual(first['fired'], ['loans_Preferential_rate'])

# ################################################################################################################################
# ################################################################################################################################

class TestChampionChallenger(unittest.TestCase):
    """ Tests two versions running side by side over one scenario set.
    """

    def test_side_by_side_kpis_and_diff(self) -> 'None':
        """ Both versions report the same KPIs over the same inputs, with the diff explaining the gap.
        """
        champion_documents = _parse(_champion_text)
        challenger_documents = _parse(_challenger_text)

        scenarios = _get_scenarios()
        kpis = [
            {'name': 'Approval rate', 'kind': KpiKind.Rate, 'field': 'approved', 'value': True},
        ]

        result = champion_challenger(champion_documents, challenger_documents, scenarios, kpis)

        champion_kpi = result['champion']['kpis'][0]
        challenger_kpi = result['challenger']['kpis'][0]

        # The challenger's higher bar approves one customer fewer.
        self.assertAlmostEqual(champion_kpi['value'], 2 / 3)
        self.assertAlmostEqual(challenger_kpi['value'], 1 / 3)

        # The diff points at the one decision that would change.
        diff = result['diff']
        self.assertEqual(diff['changed'], 1)
        self.assertEqual(diff['unchanged'], 2)

        changed_entries = []
        for entry in diff['scenarios']:
            if entry['status'] == 'changed':
                changed_entries.append(entry)

        changed = changed_entries[0]
        self.assertEqual(changed['scenario'], 'Mid score')
        self.assertListEqual(changed['fired_only_old'], ['loans_Preferential_rate'])
        self.assertListEqual(changed['fired_only_new'], ['loans_Standard_rate'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
