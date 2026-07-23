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

class TestMatchComplex(unittest.TestCase):
    """ Tests rules whose conditions combine several and-groups through or.
    """
    def setUp(self) -> 'None':
        rules_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.helper = RuleTestHelper(rules_dir)

# ################################################################################################################################

    def test_and_binds_tighter_than_or(self) -> 'None':
        """ Conditions form and-groups joined by or, so one full group is enough to match.
        """

        # The first and-group holds - high trade amount with high volatility ..
        data = {
            'trade_amount': 2000000,
            'currency_volatility': 0.06,
            'client_trading_history_months': 24,
        }
        result = self.helper.match_rule('exec_03_FX_HighValue_TradeApproval', data)
        self.assertTrue(result)
        self.assertEqual(result.then['approval_level'], 'senior_trader')

        # .. the second and-group holds - high trade amount with a short history ..
        data = {
            'trade_amount': 2000000,
            'currency_volatility': 0.01,
            'client_trading_history_months': 3,
        }
        result = self.helper.match_rule('exec_03_FX_HighValue_TradeApproval', data)
        self.assertTrue(result)

        # .. and neither group holds when volatility is low and the history is long.
        data = {
            'trade_amount': 2000000,
            'currency_volatility': 0.01,
            'client_trading_history_months': 24,
        }
        result = self.helper.match_rule('exec_03_FX_HighValue_TradeApproval', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_or_chain_matches_on_any_condition(self) -> 'None':
        """ A pure or-chain matches as soon as any single condition holds.
        """

        # Severity alone is enough ..
        data = {'incident_severity': 9, 'population_affected': 5, 'critical_infrastructure_involved': 'none'}
        result = self.helper.match_rule('exec_08_Emergency_HighPriority_Response', data)
        self.assertTrue(result)
        self.assertEqual(result.then['priority_level'], 'high')

        # .. population alone is enough ..
        data = {'incident_severity': 2, 'population_affected': 150, 'critical_infrastructure_involved': 'none'}
        result = self.helper.match_rule('exec_08_Emergency_HighPriority_Response', data)
        self.assertTrue(result)

        # .. infrastructure membership alone is enough ..
        data = {'incident_severity': 2, 'population_affected': 5, 'critical_infrastructure_involved': 'water_treatment'}
        result = self.helper.match_rule('exec_08_Emergency_HighPriority_Response', data)
        self.assertTrue(result)

        # .. and nothing at all means no match.
        data = {'incident_severity': 2, 'population_affected': 5, 'critical_infrastructure_involved': 'none'}
        result = self.helper.match_rule('exec_08_Emergency_HighPriority_Response', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_many_and_conditions(self) -> 'None':
        """ A long all-and rule needs every single condition to hold.
        """
        data = {
            'address_serviceable': True,
            'infrastructure_available': True,
            'outstanding_balance': 25,
            'service_restrictions_count': 0,
            'credit_score': 700,
        }
        result = self.helper.match_rule('exec_02_BSS_Service_Activation', data)
        self.assertTrue(result)
        self.assertEqual(result.then['installation_type'], 'standard')

        # One failing condition is enough to reject.
        data['service_restrictions_count'] = 1
        result = self.helper.match_rule('exec_02_BSS_Service_Activation', data)
        self.assertFalse(result)

# ################################################################################################################################

    def test_mixed_or_chain_with_memberships(self) -> 'None':
        """ Membership and equality conditions mix freely in an or-chain.
        """

        # A short connection time alone matches ..
        data = {
            'connecting_flight_minutes': 45,
            'passenger_status': 'regular',
            'baggage_tag_priority': 'standard',
            'special_handling_code': 'NONE',
        }
        result = self.helper.match_rule('exec_10_Airport_BaggageHandling_PriorityRouting', data)
        self.assertTrue(result)
        self.assertEqual(result.then['routing_priority'], 'expedited')

        # .. so does a special handling code from the list ..
        data = {
            'connecting_flight_minutes': 240,
            'passenger_status': 'regular',
            'baggage_tag_priority': 'standard',
            'special_handling_code': 'FRAGILE',
        }
        result = self.helper.match_rule('exec_10_Airport_BaggageHandling_PriorityRouting', data)
        self.assertTrue(result)

        # .. and unremarkable baggage does not match at all.
        data = {
            'connecting_flight_minutes': 240,
            'passenger_status': 'regular',
            'baggage_tag_priority': 'standard',
            'special_handling_code': 'NONE',
        }
        result = self.helper.match_rule('exec_10_Airport_BaggageHandling_PriorityRouting', data)
        self.assertFalse(result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
