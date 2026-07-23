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
from zato.common.test.rules import RuleTestHelper

# ################################################################################################################################
# ################################################################################################################################

class TestMatchDomainSpecific(unittest.TestCase):
    """ Tests rules modelled on concrete business domains.
    """
    def setUp(self) -> 'None':
        # The shared zrules fixtures live one level up, next to the test subdirectories.
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.helper = RuleTestHelper(rules_dir)

# ################################################################################################################################

    def test_benefit_eligibility(self) -> 'None':
        """ Benefit eligibility needs age, income and residency to line up.
        """
        data = {'applicant_age': 70, 'annual_income': 30000, 'years_of_residency': 10, 'preferred_contact_method': 'postal_mail'}
        result = self.helper.match_rule('exec_06_Government_BenefitEligibility', data)
        self.assertTrue(result)
        self.assertListEqual(result.then['eligible_programs'], ['senior_tax_relief', 'utility_assistance', 'transportation_subsidy'])

        # The notification method resolves from the applicant's own preference.
        self.assertEqual(result.then['notification_method'], 'postal_mail')

        # Too high an income means no eligibility.
        data = {'applicant_age': 70, 'annual_income': 40000, 'years_of_residency': 10, 'preferred_contact_method': 'postal_mail'}
        result = self.helper.match_rule('exec_06_Government_BenefitEligibility', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_permit_approval(self) -> 'None':
        """ Permit approval combines equality, boundaries, booleans and a default reference.
        """
        data = {
            'zoning_code': 'residential',
            'proposed_height_feet': 30,
            'proposed_setback_feet': 20,
            'environmental_concerns': False,
            'construction_year': 1995,
        }
        result = self.helper.match_rule('exec_07_Government_PermitApproval_Residential', data)
        self.assertTrue(result)
        self.assertEqual(result.then['permit_status'], 'approved')
        self.assertEqual(result.then['permit_valid_days'], 180)

        # A building older than the default review year needs a person to look at it.
        data['construction_year'] = 1930
        result = self.helper.match_rule('exec_07_Government_PermitApproval_Residential', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_gate_assignment(self) -> 'None':
        """ Gate assignment reads the aircraft list from defaults and the gate from input data.
        """
        data = {
            'aircraft_type': 'A350',
            'gate_width_meters': 50,
            'jetbridge_length_meters': 15,
            'gate_currently_available': True,
            'nearest_available_gate': 'B22',
        }
        result = self.helper.match_rule('exec_09_Airport_GateAssignment_WidebodyAircraft', data)
        self.assertTrue(result)

        # The assigned gate resolves from the input data reference.
        self.assertEqual(result.then['assigned_gate'], 'B22')
        self.assertEqual(result.then['ground_services_level'], 'premium')

        # A narrow-body aircraft type is not in the defaults list.
        data['aircraft_type'] = 'A320'
        result = self.helper.match_rule('exec_09_Airport_GateAssignment_WidebodyAircraft', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_wildlife_monitoring(self) -> 'None':
        """ Ecosystem assessment compares two input fields against each other.
        """
        data = {
            'species_diversity_index': 82,
            'previous_year_index': 75,
            'endangered_species_sightings': 3,
            'habitat_condition_score': 70,
            'invasive_species_percentage': 5,
        }
        result = self.helper.match_rule('exec_05_Environmental_WildlifeMonitoring_Biodiversity', data)
        self.assertTrue(result)
        self.assertEqual(result.then['ecosystem_status'], 'improving')

        # An index no better than last year means the field-to-field comparison fails.
        data['species_diversity_index'] = 75
        result = self.helper.match_rule('exec_05_Environmental_WildlifeMonitoring_Biodiversity', data)
        self.assertFalse(result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
