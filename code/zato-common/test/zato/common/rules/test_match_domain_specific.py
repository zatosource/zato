# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import unittest
from logging import getLogger
from pathlib import Path

# Zato
from zato.common.test.rules import RuleTestHelper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestMatchDomainSpecific(unittest.TestCase):
    """ Tests domain-specific rules with realistic data scenarios.
    """
    def setUp(self) -> 'None':
        # Initialize the rule test helper with the path to the rules directory
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)

    def test_fx_trading_rules(self) -> 'None':
        """ Test foreign exchange trading rules.
        """
        # Find FX trading rules
        fx_rules = self.helper.find_rules_with_condition('FX')

        if not fx_rules:
            # Try with trade_amount instead
            fx_rules = self.helper.find_rules_with_condition('trade_amount')

        if not fx_rules:
            self.skipTest('No FX trading rules found')

        # Use the first FX trading rule
        rule_name = fx_rules[0]
        logger.info(f'Testing FX trading rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with high_value_threshold condition
        if 'trade_amount' in rule_condition and 'high_value_threshold' in rule_condition:
            # Test with high-value trade that should require approval
            data = {
                'trade_amount': 2000000,  # High value
                'currency_volatility': 0.06,  # High volatility
                'client_trading_history_months': 3,  # Limited history
                'market_condition': 'volatile'
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched for high-risk trade')

            # Test with low-value trade that should not require approval
            data = {
                'trade_amount': 500000,  # Low value
                'currency_volatility': 0.02,  # Low volatility
                'client_trading_history_months': 12,  # Established history
                'market_condition': 'stable'
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched for low-risk trade')

            # Test boundary condition - just above threshold
            data = {
                'trade_amount': 1000001,  # Just above threshold
                'currency_volatility': 0.06,  # High volatility
                'client_trading_history_months': 3,  # Limited history
                'market_condition': 'volatile'
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched for trade just above threshold')

        # For other FX trading rules
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_manufacturing_quality_rules(self) -> 'None':
        """ Test manufacturing quality control rules.
        """
        # Find manufacturing quality rules
        manufacturing_rules = self.helper.find_rules_with_condition('Manufacturing')

        if not manufacturing_rules:
            # Try with dimensional_deviation instead
            manufacturing_rules = self.helper.find_rules_with_condition('dimensional_deviation')

        if not manufacturing_rules:
            self.skipTest('No manufacturing quality rules found')

        # Use the first manufacturing quality rule
        rule_name = manufacturing_rules[0]
        logger.info(f'Testing manufacturing quality rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with dimensional_deviation condition
        if 'dimensional_deviation' in rule_condition:
            # Test with product that should be rejected (dimensional issue)
            data = {
                'dimensional_deviation': 0.15,  # Above tolerance
                'material_strength': 450,  # Above minimum
                'surface_defect_count': 2,  # Low defects
                'tolerance_threshold': 0.1,
                'minimum_strength_requirement': 400,
                'test_result': 'pass',
                'retest_result': 'pass'
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched for dimensional issue')

            # Test with product that should be rejected (material issue)
            data = {
                'dimensional_deviation': 0.05,  # Within tolerance
                'material_strength': 350,  # Below minimum
                'surface_defect_count': 2,  # Low defects
                'tolerance_threshold': 0.1,
                'minimum_strength_requirement': 400,
                'test_result': 'pass',
                'retest_result': 'pass'
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched for material issue')

            # Test with product that should be accepted (all parameters good)
            data = {
                'dimensional_deviation': 0.05,  # Within tolerance
                'material_strength': 450,  # Above minimum
                'surface_defect_count': 2,  # Low defects
                'tolerance_threshold': 0.1,
                'minimum_strength_requirement': 400,
                'test_result': 'pass',
                'retest_result': 'pass'
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched for good product')

        # For other manufacturing quality rules
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_government_benefit_rules(self) -> 'None':
        """ Test government benefit eligibility rules.
        """
        # Find government benefit rules
        government_rules = self.helper.find_rules_with_condition('Government')

        if not government_rules:
            # Try with applicant_age instead
            government_rules = self.helper.find_rules_with_condition('applicant_age')

        if not government_rules:
            self.skipTest('No government benefit rules found')

        # Use the first government benefit rule
        rule_name = government_rules[0]
        logger.info(f'Testing government benefit rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with applicant_age condition
        if 'applicant_age' in rule_condition:
            # Test with eligible senior
            data = {
                'applicant_age': 70,  # Above 65
                'annual_income': 25000,  # Below threshold
                'years_of_residency': 10  # Above minimum
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched for eligible senior')

            # Test with ineligible person (too young)
            data = {
                'applicant_age': 60,  # Below 65
                'annual_income': 25000,  # Below threshold
                'years_of_residency': 10  # Above minimum
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched for person too young')

            # Test with ineligible person (income too high)
            data = {
                'applicant_age': 70,  # Above 65
                'annual_income': 40000,  # Above threshold
                'years_of_residency': 10  # Above minimum
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched for income too high')

            # Test with ineligible person (residency too short)
            data = {
                'applicant_age': 70,  # Above 65
                'annual_income': 25000,  # Below threshold
                'years_of_residency': 3  # Below minimum
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched for residency too short')

        # For other government benefit rules
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

    def test_emergency_response_rules(self) -> 'None':
        """ Test emergency response prioritization rules.
        """
        # Find emergency response rules
        emergency_rules = self.helper.find_rules_with_condition('Emergency')

        if not emergency_rules:
            # Try with incident_severity instead
            emergency_rules = self.helper.find_rules_with_condition('incident_severity')

        if not emergency_rules:
            self.skipTest('No emergency response rules found')

        # Use the first emergency response rule
        rule_name = emergency_rules[0]
        logger.info(f'Testing emergency response rule: {rule_name}')

        # Get the rule condition to determine what data to use
        rule_condition = self.helper.get_rule_condition(rule_name)
        logger.info(f'Rule condition: {rule_condition}')

        # For a rule with incident_severity condition
        if 'incident_severity' in rule_condition:
            # Test with high-priority incident (high severity)
            data = {
                'incident_severity': 9,  # High severity
                'population_affected': 50,  # Moderate population
                'critical_infrastructure_involved': 'hospital'  # Critical infrastructure
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched for high-severity incident')

            # Test with high-priority incident (large population)
            data = {
                'incident_severity': 6,  # Moderate severity
                'population_affected': 200,  # Large population
                'critical_infrastructure_involved': 'residential'  # Non-critical infrastructure
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched for large population incident')

            # Test with high-priority incident (critical infrastructure)
            data = {
                'incident_severity': 6,  # Moderate severity
                'population_affected': 50,  # Moderate population
                'critical_infrastructure_involved': 'power_plant'  # Critical infrastructure
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertTrue(result, f'Rule {rule_name} should have matched for critical infrastructure incident')

            # Test with low-priority incident
            data = {
                'incident_severity': 5,  # Low severity
                'population_affected': 20,  # Small population
                'critical_infrastructure_involved': 'commercial'  # Non-critical infrastructure
            }

            result = self.helper.match_rule(rule_name, data)
            self.assertFalse(result, f'Rule {rule_name} should not have matched for low-priority incident')

        # For other emergency response rules
        else:
            logger.info(f'Skipping specific tests for {rule_name} - would need custom test data')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
