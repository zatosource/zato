# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from datetime import datetime
from pathlib import Path
from statistics import mean, median, stdev

# Zato
from zato.common.rules.api import RulesManager
from zato.common.typing_ import any_, anydict, dict_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ASCIITable:
    """ Simple ASCII table generator without external dependencies. """
    
    @staticmethod
    def make_table(data, headers):
        """ Create an ASCII table with the given data and headers. """
        if not data:
            return "No data available"
        
        # Convert all data to strings
        str_data = [[str(cell) for cell in row] for row in data]
        
        # Calculate column widths
        col_widths = [max(len(h), max([len(row[i]) for row in str_data])) 
                     for i, h in enumerate(headers)]
        
        # Create the header row
        header_row = '| ' + ' | '.join(h.ljust(w) for h, w in zip(headers, col_widths)) + ' |'
        separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
        separator = separator.replace('+-+', '---')
        
        # Create the data rows
        data_rows = ['| ' + ' | '.join(cell.ljust(w) for cell, w in zip(row, col_widths)) + ' |' 
                    for row in str_data]
        
        # Combine all parts
        table = [separator, header_row, separator] + data_rows + [separator]
        
        return '\n'.join(table)

class BarChart:
    """ Simple ASCII bar chart generator without external dependencies. """
    
    @staticmethod
    def render(data, title='', xlabel='', ylabel='', width=60, height=10):
        """ Create an ASCII bar chart with the given data. """
        if not data:
            return "No data available"
        
        # Extract labels and values
        labels, values = zip(*data)
        
        # Calculate the maximum value for scaling
        max_value = max(values)
        
        # Calculate the scale factor
        scale = height / max_value if max_value > 0 else 1
        
        # Create the chart
        chart = []
        
        # Add title
        if title:
            chart.append(title.center(width))
            chart.append('')
        
        # Find the maximum label length for alignment
        max_label_length = max(len(label) for label in labels)
        
        # Create the bars
        for i, (label, value) in enumerate(data):
            bar_height = int(value * scale)
            bar = '█' * bar_height
            # Format the value with consistent spacing for 3 digits
            value_str = f"{value:8.4f}"
            chart.append(f"{label:{max_label_length}} | {bar} {value_str}")
        
        # Add axes labels
        if xlabel or ylabel:
            chart.append('')
            if xlabel:
                chart.append(xlabel.center(width))
            if ylabel:
                chart.append(f"Note: {ylabel}")
        
        return '\n'.join(chart)

# ################################################################################################################################
# ################################################################################################################################

class RulePerformanceTester:
    """ Utility class for testing rule engine performance. """
    
    def __init__(self, rules_dir=None, pattern=None):
        """ Initialize the performance tester.
        
        Args:
            rules_dir: Directory containing rule files (or parent directory of 'perf' subdirectory)
            pattern: Pattern to match rule files (e.g., 'perf_010_rules_*.zrules')
        """
        self.rules_dir = Path(rules_dir) if rules_dir else Path(os.path.dirname(os.path.abspath(__file__)))
        self.pattern = pattern
        self.results = []
        
        # Find the perf directory
        self.perf_dir = self.rules_dir / 'zrules' / 'perf'
        if not self.perf_dir.exists():
            self.perf_dir = self.rules_dir / 'perf'
            if not self.perf_dir.exists():
                raise ValueError(f"Performance test directory not found at {self.perf_dir}")
        
        print(f"Using performance test directory: {self.perf_dir}")
        
        # Find all matching rule files
        self.rule_files = self._find_rule_files()
        print(f"Found {len(self.rule_files)} rule files matching pattern {self.pattern or '*'}")
        
        # Generate test data
        self.test_data = self._generate_test_data()
    
    def _find_rule_files(self):
        """ Find all rule files matching the pattern. """
        if self.pattern:
            return list(self.perf_dir.glob(self.pattern))
        else:
            return list(self.perf_dir.glob('*.zrules'))
    
    def _generate_test_data(self):
        """ Generate test data for each rule file. """
        # Common test data that should match at least one rule in each file
        base_data = {
            # Common fields - these are used in common conditions
            'account_status': 'active',
            'customer_id': 'AB123456',
            'customer_type': 'business',
            'is_contract_signed': True,
            'monthly_spend': 600,
            'region': 'EMEA',
            'service_level': 'premium',
            'subscription_months': 12,
            'usage_percentage': 80,
            'customer_segment': 'enterprise',
            
            # Specific fields for various rules
            'support_tickets_open': 2,
            'usage_decline_months': 4,
            'upgrade_eligibility_score': 8,
            'peak_usage_percentage': 80,
            'capacity_threshold': 75,
            'outage_duration_minutes': 45,
            'min_outage_minutes': 30,
            'services_subscribed': 2,
            'equipment_age_months': 36,
            'current_platform': 'PSTN',
            'legacy_platforms': ['TDM', 'PSTN', 'ISDN'],
            'contract_end_days': 60,
            'customer_industry': 'healthcare',
            'iot_compatible_industries': ['manufacturing', 'healthcare', 'logistics', 'retail', 'utilities'],
            'billing_complaints': 2,
            'churn_prediction_score': 0.8,
            'bandwidth_utilization': 85,
            'credit_score': 750,
            'business_customers_affected': 60,
            'network_segment_congestion': True,
            'projected_growth_rate': 7,
            'business_impact_level': 3,
            'fault_responsibility': 'provider',
            'sla_breach': True,
            'cross_sell_propensity': 0.7,
            'last_upsell_attempt_days': 120,
            'service_usage_complementary': True,
            'hardware_compatibility_new_features': False,
            'service_calls_equipment': 2,
            'has_custom_integrations': False,
            'migration_complexity_score': 5,
            'competitive_pressure_score': 4,
            'customer_lifetime_value': 60000,
            'data_service_subscribed': True,
            'digital_transformation_score': 7,
            'monthly_data_usage': 600,
            'technology_adoption_score': 8,
            'priority_support_eligible': True,
            'critical_business_process': True,
            'dedicated_support_eligible': True,
            'satisfaction_score': 6,
            'retention_score': 5,
            'competitor_mentions_support': 1,
            'payment_method': 'auto',
            
            # Additional fields based on error message
            'growth_trajectory_positive': True,
            'payment_history_months': 24,
            'customer_complaints_capacity': 15,
            'last_upgrade_months': 18,
            'customer_reported_issue': True,
            'multiple_services_affected': True,
            'service_affected': 'critical',
            'customer_growth_phase': 'expansion',
            'contract_remaining_months': 18,
            'current_equipment_model_discontinued': True,
            'upgrade_program_eligible': True,
            'platform_support_end_months': 6,
            'service_compatibility_new_platform': True,
            'technology_refresh_budget_approved': True,
            'market_share_strategic_account': True,
            'price_sensitivity_score': 8,
            'renewal_propensity_score': 0.6,
            'subscription_type': 'platinum',
            'competitor_iot_mentions': 2,
            'iot_inquiries': 3,
            
            # Default values
            'high_risk_threshold': 3,
            'premium_subscription_types': ['platinum', 'gold', 'enterprise'],
            'min_subscription_months': 6,
            'high_priority_regions': ['EMEA', 'APAC', 'NA'],
            'legacy_platforms': ['TDM', 'PSTN', 'ISDN'],
            'capacity_threshold': 75,
            'min_outage_minutes': 30,
            'iot_compatible_industries': ['manufacturing', 'healthcare', 'logistics', 'retail', 'utilities'],
            'support_tiers': ['standard', 'premium', 'platinum'],
            'response_time_thresholds': {'standard': 24, 'premium': 8, 'platinum': 4}
        }
        
        return base_data
    
    def test_file(self, file_path, iterations=3, runs_per_iteration=1000):
        """ Test a single rule file and return performance metrics. """
        # Extract file characteristics from the name
        # Format: perf_010_rules_XXX_conditions_YYY_common.zrules
        file_name = file_path.stem
        parts = file_name.split('_')
        
        # Extract metrics from filename
        num_rules = int(parts[1])
        num_conditions = int(parts[3])
        num_common = int(parts[5])
        
        print(f"Testing {file_name} with {num_rules} rules, {num_conditions} conditions, {num_common} common conditions")
        
        # Create a new rules manager for this test
        rules_manager = RulesManager()
        
        # Load the rules from the file
        try:
            rules_manager.load_rules_from_file(file_path)
            print(f"Loaded {len(rules_manager._all_rules)} rules from {file_name}")
        except Exception as e:
            print(f"Error loading rules from {file_name}: {e}")
            return None
        
        # Get all rule names for this file
        rule_names = list(rules_manager._all_rules.keys())
        if not rule_names:
            print(f"No rules found in {file_name}, skipping")
            return None
        
        # Run the test multiple times to get reliable results
        match_times = []
        match_results = []
        
        for i in range(iterations):
            print(f"Running iteration {i+1}/{iterations}...")
            
            # Measure the time it takes to match all rules multiple times
            start_time = time.time()
            
            # Run multiple matching operations to get measurable times
            for j in range(runs_per_iteration):
                # Try to match each rule individually
                for rule_name in rule_names:
                    result = rules_manager[rule_name].match(self.test_data)
                    if result and j == 0:  # Only collect match results once
                        match_results.append(rule_name)
            
            end_time = time.time()
            match_time = ((end_time - start_time) * 1000) / runs_per_iteration  # Average time per run in ms
            match_times.append(match_time)
            
            print(f"Iteration {i+1} completed in {match_time:.4f}ms per run")
        
        # Calculate statistics
        avg_time = mean(match_times)
        median_time = median(match_times)
        min_time = min(match_times)
        max_time = max(match_times)
        std_dev = stdev(match_times) if len(match_times) > 1 else 0
        
        # Store the results
        result = {
            'file_name': file_name,
            'num_rules': num_rules,
            'num_conditions': num_conditions,
            'num_common': num_common,
            'avg_time': avg_time,
            'median_time': median_time,
            'min_time': min_time,
            'max_time': max_time,
            'std_dev': std_dev,
            'matched_rules': len(set(match_results))
        }
        
        print(f"Results for {file_name}: avg={avg_time:.4f}ms, median={median_time:.4f}ms, matched={len(set(match_results))}")
        return result
    
    def run_tests(self, iterations=3, runs_per_iteration=1000):
        """ Run performance tests for all matching rule files. """
        for file_path in self.rule_files:
            result = self.test_file(file_path, iterations, runs_per_iteration)
            if result:
                self.results.append(result)
    
    def display_results(self):
        """ Display the performance test results in an ASCII table. """
        if not self.results:
            print("No results to display. Run tests first.")
            return
        
        # Sort results by file name
        sorted_results = sorted(self.results, key=lambda x: x['file_name'])
        
        # Create a table
        table_data = []
        for result in sorted_results:
            table_data.append([
                result['file_name'],
                result['num_rules'],
                result['num_conditions'],
                result['num_common'],
                f"{result['avg_time']:.4f}",
                f"{result['median_time']:.4f}",
                f"{result['min_time']:.4f}",
                f"{result['max_time']:.4f}",
                f"{result['std_dev']:.4f}",
                result['matched_rules']
            ])
        
        # Define the table headers
        headers = [
            'File Name',
            'Rules',
            'Conditions',
            'Common',
            'Avg (ms)',
            'Median (ms)',
            'Min (ms)',
            'Max (ms)',
            'StdDev (ms)',
            'Matched'
        ]
        
        # Display the table
        print('\nPerformance Test Results (sorted by file name):')
        print(ASCIITable.make_table(table_data, headers))
        print('\nNote: StdDev (Standard Deviation) measures the variability in timing results.')
        print('      Lower values indicate more consistent/reproducible performance.')
        
        # Create a bar chart with more readable labels and consistent formatting
        print('\nPerformance Comparison Chart (milliseconds):')
        chart_data = [(f"{result['num_conditions']:003d} conditions, {result['num_common']:003d} common", result['avg_time']) 
                     for result in sorted(sorted_results, key=lambda x: x['avg_time'])]
        print(BarChart.render(
            chart_data, 
            title='Average Rule Matching Time (milliseconds)',
            xlabel='Rule Configuration',
            ylabel='Time in milliseconds',
            width=80,
            height=15
        ))
        
        # Add information about reproducibility
        print('\nTest Reproducibility:')
        print('- Match results are deterministic and should be consistent across runs')
        print('- Timing results may vary slightly based on system load')
        print('- Standard deviation (StdDev) values indicate timing consistency')
