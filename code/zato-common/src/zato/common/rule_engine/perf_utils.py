# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
import signal
import sys
from pathlib import Path
from statistics import mean, median, stdev

# Zato
from zato.common.rule_engine.api import RulesManager
from zato.common.rule_engine.perf_display import Fore, PerfDisplay, Style

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intlist

# ################################################################################################################################
# ################################################################################################################################


# ################################################################################################################################
# ################################################################################################################################


# ################################################################################################################################
# ################################################################################################################################

class RulePerformanceTester(PerfDisplay):
    """ Utility class for testing rule engine performance. """

    def __init__(self, rules_dir:'Path | None'=None, pattern:'str | None'=None) -> 'None':
        """ Initialize the performance tester.

        Args:
            rules_dir: Directory containing rule files (or parent directory of 'perf' subdirectory)
            pattern: Pattern to match rule files (e.g., 'perf_010_rules_*.zrules')
        """
        self.rules_dir = Path(rules_dir) if rules_dir else Path(os.path.dirname(os.path.abspath(__file__)))
        self.pattern = pattern
        self.results = []
        self.rule_groups = {}  # Group results by rule count
        self.group_times = {}  # Track time spent on each group
        self.total_start_time = time.time()
        self.interrupted = False

        # Set up signal handler for Ctrl+C
        self._setup_signal_handler()

        # Find the perf directory
        self.perf_dir = self.rules_dir / 'zrules' / 'perf'
        if not self.perf_dir.exists():
            self.perf_dir = self.rules_dir / 'perf'
            if not self.perf_dir.exists():
                raise ValueError(f"Performance test directory not found at {self.perf_dir}")

        print(f"{Fore.CYAN}Using performance test directory: {self.perf_dir}{Style.RESET_ALL}")

        # Find all matching rule files and sort them alphabetically
        self.rule_files = sorted(self._find_rule_files())
        print(f"{Fore.GREEN}Found {len(self.rule_files)} rule files matching pattern {self.pattern or '*'}{Style.RESET_ALL}")

        # Generate test data
        self.test_data = self._generate_test_data()

    def _find_rule_files(self) -> 'anylist':
        """ Find all rule files matching the pattern. """
        if self.pattern:
            return list(self.perf_dir.glob(self.pattern))
        else:
            return list(self.perf_dir.glob('*.zrules'))

    def _generate_test_data(self) -> 'anydict':
        """ Generate test data for each rule file. """
        # Common test data that should match multiple conditions in each file
        # We'll match 3 conditions for 5-condition rules and 5 conditions for 10-condition rules
        base_data = {
            # Common fields - these are used in common conditions
            # We'll make account_status active to match the first common condition
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

            # Specific fields for various rules - we'll ensure these match
            'support_tickets_open': 2,
            'usage_decline_months': 4,
            'upgrade_eligibility_score': 8,
            'peak_usage_percentage': 80,
            'capacity_threshold': 75,
            'min_outage_minutes': 30,
            'iot_compatible_industries': ['manufacturing', 'healthcare', 'logistics', 'retail', 'utilities'],
            'outage_duration_minutes': 45,
            'services_subscribed': 2,
            'equipment_age_months': 36,
            'current_platform': 'CABLE',
            'supported_platforms': ['FIBER', 'CABLE', 'FIXED_WIRELESS'],
            'contract_end_days': 60,
            'customer_industry': 'healthcare',
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
            'support_tiers': ['standard', 'premium', 'platinum'],
            'response_time_thresholds': {'standard': 24, 'premium': 8, 'platinum': 4}
        }

        # We'll track how many input parameters we expect to match
        self.expected_matches = {
            5: 3,  # For 5-condition rules, we expect 3 conditions to match
            10: 5   # For 10-condition rules, we expect 5 conditions to match
        }

        return base_data

    def _setup_signal_handler(self) -> 'None':
        """ Set up a signal handler for Ctrl+C to gracefully exit the tests. """
        def signal_handler(sig:'int', frame:'any_') -> 'None':
            print(f"\n{Fore.YELLOW}Interrupted by user. Finishing current test and displaying results...{Style.RESET_ALL}")
            self.interrupted = True

        # Register the signal handler for SIGINT (Ctrl+C)
        _ = signal.signal(signal.SIGINT, signal_handler)

    def test_file(self, file_path:'Path', iterations:'int'=3, runs_per_iteration:'int'=1000) -> 'anydict | None':
        """ Test a single rule file and return performance metrics. """
        # Extract file characteristics from the name
        # Format: perf_010_rules_XXX_conditions_YYY_common.zrules
        file_name = file_path.stem
        parts = file_name.split('_')

        # Extract metrics from filename
        num_rules = int(parts[1])
        num_conditions = int(parts[3])
        num_common = int(parts[5])

        # Determine expected matching conditions based on number of conditions per rule
        expected_matching_conditions = self.expected_matches.get(num_conditions, 1)

        # Use in-place printing for progress
        shape = f'{num_rules} rules, {num_conditions} conditions, {num_common} common conditions'
        progress = f'\r{Fore.YELLOW}Testing {file_name} with {shape}{" " * 20}{Style.RESET_ALL}'
        _ = sys.stdout.write(progress)
        _ = sys.stdout.flush()

        # Create a new rules manager for this test
        rules_manager = RulesManager()

        # Load the rules from the file
        try:
            _ = rules_manager.load_rules_from_file(file_path)
            _ = sys.stdout.write(f"\r{Fore.YELLOW}Testing {file_name} - Loaded {len(rules_manager._all_rules)} rules{' ' * 40}{Style.RESET_ALL}")
            _ = sys.stdout.flush()
        except Exception as e:
            print(f"\r{Fore.RED}Error loading rules from {file_name}: {e}{Style.RESET_ALL}")
            return None

        # Get all rule names for this file
        rule_names = list(rules_manager._all_rules.keys())
        if not rule_names:
            print(f"\r{Fore.RED}No rules found in {file_name}, skipping{Style.RESET_ALL}")
            return None

        # Run the test multiple times to get reliable results
        match_times = []
        match_results = []

        for i in range(iterations):
            # Update progress in-place
            _ = sys.stdout.write(f"\r{Fore.YELLOW}Testing {file_name} - Running iteration {i+1}/{iterations}{' ' * 40}{Style.RESET_ALL}")
            _ = sys.stdout.flush()

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

        # Calculate statistics
        avg_time = mean(match_times)
        median_time = median(match_times)
        min_time = min(match_times)
        max_time = max(match_times)
        std_dev = stdev(match_times) if len(match_times) > 1 else 0

        # Calculate total execution time for the whole file (per run)
        total_time = avg_time * num_rules

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
            'matched_rules': len(set(match_results)),
            'matching_conditions': expected_matching_conditions,
            'total_time': total_time  # Total time for all rules in the file
        }

        # Group results by rule count
        if num_rules not in self.rule_groups:
            self.rule_groups[num_rules] = []
            self.group_times[num_rules] = {'start': time.time(), 'end': None}
        self.rule_groups[num_rules].append(result)

        # Print completion message with proper spacing
        matched_str = f'matched={len(set(match_results))}'
        timings = f'avg={avg_time:.4f}ms, total={total_time:.4f}ms'
        completion = f'\r{Fore.GREEN}Completed {file_name}: {Fore.CYAN}{timings}, {Fore.MAGENTA}{matched_str}{" " * 40}{Style.RESET_ALL}'
        print(completion)

        return result

    def filter_by_rule_counts(self, rule_counts:'intlist') -> 'None':
        """ Filter the rule files to only include those with the specified rule counts. """
        filtered_files = []

        for file_path in self.rule_files:
            file_name = os.path.basename(file_path)

            # Extract the rule count from the file name
            # Format: perf_NNN_rules_...
            parts = file_name.split('_')
            if len(parts) >= 3 and parts[0] == 'perf' and parts[2] == 'rules':
                try:
                    rule_count = int(parts[1])
                    if rule_count in rule_counts:
                        filtered_files.append(file_path)
                except ValueError:
                    # Skip files that don't have a valid rule count
                    pass

        # Update the rule files list with the filtered list
        self.rule_files = filtered_files
        print(f"Found {len(self.rule_files)} rule files matching the specified rule counts")

    def run_tests(self, iterations:'int'=3, runs_per_iteration:'int'=1000) -> 'None':
        """ Run performance tests for all matching rule files. """
        # Group files by rule count for ordered processing
        file_groups = {}
        for file_path in self.rule_files:
            file_name = os.path.basename(file_path)
            # Extract rule count from file name (perf_NNN_rules_...)
            parts = file_name.split('_')
            if len(parts) >= 3 and parts[0] == 'perf' and parts[2] == 'rules':
                try:
                    rule_count = int(parts[1])
                    if rule_count not in file_groups:
                        file_groups[rule_count] = []
                    file_groups[rule_count].append(file_path)
                except ValueError:
                    # Skip files that don't have a valid rule count
                    pass

        # Process files in order of increasing rule count
        self.total_start_time = time.time()
        total_files = sum(len(files) for files in file_groups.values())
        processed_files = 0

        print(f"\n{Fore.CYAN}{'=' * 30} Rule Engine Performance Tests {'=' * 30}{Style.RESET_ALL}")
        print(f"Found {total_files} rule files to test across {len(file_groups)} rule counts")
        print(f"Running {iterations} iterations with {runs_per_iteration} runs per iteration")
        print("Press Ctrl+C at any time to stop testing and see results for completed tests\n")

        for rule_count in sorted(file_groups.keys()):
            files = file_groups[rule_count]
            print(f"\n{Fore.CYAN}Testing {len(files)} files with {rule_count} rules...{Style.RESET_ALL}")

            group_start_time = time.time()
            group_results = []

            for file_path in files:
                if self.interrupted:
                    print(f"\n{Fore.YELLOW}Interrupted. Skipping remaining tests.{Style.RESET_ALL}")
                    break

                processed_files += 1
                file_name = os.path.basename(file_path)
                print(f"  {Fore.GREEN}Testing {file_name} ({processed_files}/{total_files}){Style.RESET_ALL}")

                try:
                    result = self.test_file(file_path, iterations, runs_per_iteration)
                    self.results.append(result)
                    group_results.append(result)
                except Exception as e:
                    print(f"  {Fore.RED}Error testing {file_name}: {e}{Style.RESET_ALL}")

            if group_results:
                group_time = time.time() - group_start_time
                self.group_times[rule_count] = group_time
                print(f"  {Fore.CYAN}Completed {len(group_results)} tests with {rule_count} rules in {group_time:.2f} seconds{Style.RESET_ALL}")

                # Display results for this group
                self._display_group_results(rule_count)

            if self.interrupted:
                break

        # Display results
        if self.results:
            self.display_results()
        else:
            print(f"\n{Fore.RED}No test results to display. All tests failed or were skipped.{Style.RESET_ALL}")

