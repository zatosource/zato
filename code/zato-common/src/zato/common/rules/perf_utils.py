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
from datetime import datetime
from pathlib import Path
from statistics import mean, median, stdev

# Zato
from zato.common.rules.api import RulesManager

# Add colorama for terminal colors
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # Create dummy classes if colorama is not available
    class DummyFore:
        def __getattr__(self, name):
            return ''
    class DummyStyle:
        def __getattr__(self, name):
            return ''
    Fore = DummyFore()
    Style = DummyStyle()

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

    def _find_rule_files(self):
        """ Find all rule files matching the pattern. """
        if self.pattern:
            return list(self.perf_dir.glob(self.pattern))
        else:
            return list(self.perf_dir.glob('*.zrules'))

    def _generate_test_data(self):
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
            'current_platform': 'PSTN',
            'legacy_platforms': ['TDM', 'PSTN', 'ISDN'],
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
            'legacy_platforms': ['TDM', 'PSTN', 'ISDN'],
            'capacity_threshold': 75,
            'min_outage_minutes': 30,
            'iot_compatible_industries': ['manufacturing', 'healthcare', 'logistics', 'retail', 'utilities'],
            'support_tiers': ['standard', 'premium', 'platinum'],
            'response_time_thresholds': {'standard': 24, 'premium': 8, 'platinum': 4}
        }

        # We'll track how many input parameters we expect to match
        self.expected_matches = {
            5: 3,  # For 5-condition rules, we expect 3 conditions to match
            10: 5   # For 10-condition rules, we expect 5 conditions to match
        }

        return base_data

    def _setup_signal_handler(self):
        """ Set up a signal handler for Ctrl+C to gracefully exit the tests. """
        def signal_handler(sig, frame):
            print(f"\n{Fore.YELLOW}Interrupted by user. Finishing current test and displaying results...{Style.RESET_ALL}")
            self.interrupted = True

        # Register the signal handler for SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)

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

        # Determine expected matching conditions based on number of conditions per rule
        expected_matching_conditions = self.expected_matches.get(num_conditions, 1)

        # Use in-place printing for progress
        sys.stdout.write(f"\r{Fore.YELLOW}Testing {file_name} with {num_rules} rules, {num_conditions} conditions, {num_common} common conditions{' ' * 20}{Style.RESET_ALL}")
        sys.stdout.flush()

        # Create a new rules manager for this test
        rules_manager = RulesManager()

        # Load the rules from the file
        try:
            rules_manager.load_rules_from_file(file_path)
            sys.stdout.write(f"\r{Fore.YELLOW}Testing {file_name} - Loaded {len(rules_manager._all_rules)} rules{' ' * 40}{Style.RESET_ALL}")
            sys.stdout.flush()
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
            sys.stdout.write(f"\r{Fore.YELLOW}Testing {file_name} - Running iteration {i+1}/{iterations}{' ' * 40}{Style.RESET_ALL}")
            sys.stdout.flush()

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
        matched_str = f"matched={len(set(match_results))}"
        print(f"\r{Fore.GREEN}Completed {file_name}: {Fore.CYAN}avg={avg_time:.4f}ms, total={total_time:.4f}ms, {Fore.MAGENTA}{matched_str}{' ' * 40}{Style.RESET_ALL}")

        return result

    def filter_by_rule_counts(self, rule_counts):
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

    def run_tests(self, iterations=3, runs_per_iteration=1000):
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
        print(f"Press Ctrl+C at any time to stop testing and see results for completed tests\n")

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

    def _display_group_results(self, rule_count):
        """ Display results for a specific rule count group. """
        if rule_count not in self.rule_groups or not self.rule_groups[rule_count]:
            return

        print(f"\n{Fore.CYAN}{'=' * 30} Performance Results for {rule_count} Rules {'=' * 30}{Style.RESET_ALL}")

        # Sort results by common conditions
        sorted_results = sorted(self.rule_groups[rule_count], key=lambda x: (x['num_conditions'], x['num_common']))

        # Create a table for this group
        table_data = []
        for result in sorted_results:
            table_data.append([
                result['file_name'],
                result['num_conditions'],
                result['num_common'],
                result['matching_conditions'],
                f"{result['avg_time']:.4f}",
                f"{result['total_time']:.4f}",
                f"{result['matched_rules']}"
            ])

        # Define the table headers
        headers = [
            'File Name',
            'Conditions',
            'Common',
            'Matching',
            'Avg (ms)',
            'Total (ms)',
            'Matched'
        ]

        # Display the table
        print(ASCIITable.make_table(table_data, headers))

        # Create side-by-side bar charts for average and total time
        avg_chart_data = [(f"{rule_count:003d} rules, {result['num_conditions']:003d} cond, {result['num_common']:003d} common", result['avg_time'])
                         for result in sorted(sorted_results, key=lambda x: x['avg_time'])]

        total_chart_data = [(f"{rule_count:003d} rules, {result['num_conditions']:003d} cond, {result['num_common']:003d} common", result['total_time'])
                           for result in sorted(sorted_results, key=lambda x: x['total_time'])]

        # Find the maximum label length for alignment
        max_label_length = max(len(label) for label, _ in avg_chart_data)

        # Calculate scaling factors for the bars
        max_avg_value = max(value for _, value in avg_chart_data)
        max_total_value = max(value for _, value in total_chart_data)
        avg_scale = 30 / max_avg_value if max_avg_value > 0 else 0
        total_scale = 30 / max_total_value if max_total_value > 0 else 0

        # Define fixed column widths
        avg_column_width = 80  # Width for the average time column

        # Print headers for the charts
        print(f"\n{Fore.CYAN}Average Time per Rule (ms){' ' * (avg_column_width - 25)}{Fore.CYAN}Total File Execution Time (ms){Style.RESET_ALL}")
        print(f"{'-' * avg_column_width}{'-' * 50}")

        # Print the bars side by side with fixed column widths
        for (avg_label, avg_value), (total_label, total_value) in zip(
            sorted(avg_chart_data, key=lambda x: x[1]),
            sorted(total_chart_data, key=lambda x: x[1])
        ):
            # Create the bars
            avg_bar_length = int(avg_value * avg_scale)
            total_bar_length = int(total_value * total_scale)

            avg_bar = '█' * avg_bar_length
            total_bar = '█' * total_bar_length

            # Format the values with consistent spacing
            avg_value_str = f"{avg_value:8.4f}"
            total_value_str = f"{total_value:8.4f}"

            # Print the average time bar with fixed width
            avg_part = f"{avg_label:{max_label_length}} | {avg_bar} {avg_value_str}"
            # Pad to fixed width
            avg_part = f"{avg_part:{avg_column_width}}"

            # Print the total time bar
            total_part = f"{total_label:{max_label_length}} | {total_bar} {total_value_str}"

            # Print both parts
            print(f"{avg_part}{total_part}")

        # Display group timing information
        if rule_count in self.group_times:
            duration = self.group_times[rule_count]
            print(f"\n{Fore.YELLOW}Group test time: {Fore.CYAN}{duration:.2f} seconds{Style.RESET_ALL}")

    def display_results(self):
        """ Display the performance test results in an ASCII table. """
        if not self.results:
            print(f"{Fore.RED}No results to display. Run tests first.{Style.RESET_ALL}")
            return

        # Sort results by rule count, then conditions, then common conditions
        sorted_results = sorted(self.results, key=lambda x: (x['num_rules'], x['num_conditions'], x['num_common']))

        # Create a table
        table_data = []
        for result in sorted_results:
            table_data.append([
                result['file_name'],
                result['num_rules'],
                result['num_conditions'],
                result['num_common'],
                result['matching_conditions'],
                f"{result['avg_time']:.4f}",
                f"{result['total_time']:.4f}",
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
            'Matching',
            'Avg (ms)',
            'Total (ms)',
            'Median (ms)',
            'Min (ms)',
            'Max (ms)',
            'StdDev (ms)',
            'Matched'
        ]

        # Display the combined table
        print(f"\n{Fore.CYAN}{'=' * 30} Combined Performance Results {'=' * 30}{Style.RESET_ALL}")
        print(ASCIITable.make_table(table_data, headers))

        # Create side-by-side bar charts for average and total time
        avg_chart_data = [(f"{result['num_rules']:003d} rules, {result['num_conditions']:003d} cond, {result['num_common']:003d} common", result['avg_time'])
                         for result in sorted(sorted_results, key=lambda x: x['avg_time'])]

        total_chart_data = [(f"{result['num_rules']:003d} rules, {result['num_conditions']:003d} cond, {result['num_common']:003d} common", result['total_time'])
                           for result in sorted(sorted_results, key=lambda x: x['total_time'])]

        # Find the maximum label length for alignment
        max_label_length = max(len(label) for label, _ in avg_chart_data)

        # Calculate scaling factors for the bars
        max_avg_value = max(value for _, value in avg_chart_data)
        max_total_value = max(value for _, value in total_chart_data)
        avg_scale = 30 / max_avg_value if max_avg_value > 0 else 0
        total_scale = 30 / max_total_value if max_total_value > 0 else 0

        # Define fixed column widths
        avg_column_width = 80  # Width for the average time column

        # Print headers for the charts
        print(f"\n{Fore.CYAN}Average Time per Rule (ms){' ' * (avg_column_width - 25)}{Fore.CYAN}Total File Execution Time (ms){Style.RESET_ALL}")
        print(f"{'-' * avg_column_width}{'-' * 50}")

        # Print the bars side by side with fixed column widths
        for (avg_label, avg_value), (total_label, total_value) in zip(
            sorted(avg_chart_data, key=lambda x: x[1]),
            sorted(total_chart_data, key=lambda x: x[1])
        ):
            # Create the bars
            avg_bar_length = int(avg_value * avg_scale)
            total_bar_length = int(total_value * total_scale)

            avg_bar = '█' * avg_bar_length
            total_bar = '█' * total_bar_length

            # Format the values with consistent spacing
            avg_value_str = f"{avg_value:8.4f}"
            total_value_str = f"{total_value:8.4f}"

            # Print the average time bar with fixed width
            avg_part = f"{avg_label:{max_label_length}} | {avg_bar} {avg_value_str}"
            # Pad to fixed width
            avg_part = f"{avg_part:{avg_column_width}}"

            # Print the total time bar
            total_part = f"{total_label:{max_label_length}} | {total_bar} {total_value_str}"

            # Print both parts
            print(f"{avg_part}{total_part}")

        # Add total time information
        total_time = time.time() - self.total_start_time
        print(f"\n{Fore.YELLOW}Total test time: {Fore.CYAN}{total_time:.2f} seconds{Style.RESET_ALL}")

        # Generate a plain English explanation and save to a file in the temp directory
        self._save_plain_text_summary(sorted_results, total_time)

    def _save_plain_text_summary(self, sorted_results, total_time):
        """ Generate a plain English explanation of the test results and save to a file. """
        # Import tempfile here to avoid global import
        import tempfile

        # Get the fastest and slowest configurations
        by_avg_time = sorted(sorted_results, key=lambda x: x['avg_time'])
        fastest = by_avg_time[0]
        slowest = by_avg_time[-1]

        # Get the average time across all tests
        all_avg_times = [result['avg_time'] for result in sorted_results]
        overall_avg = mean(all_avg_times) if all_avg_times else 0

        # Group results by rule count
        rule_groups = {}
        for result in sorted_results:
            rule_count = result['num_rules']
            if rule_count not in rule_groups:
                rule_groups[rule_count] = []
            rule_groups[rule_count].append(result)

        # Generate the explanation
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        explanation = f"""# Zato Rule Engine Performance Test Results

Test Date: {now}

## Summary

The performance tests were run on {len(sorted_results)} different rule configurations,
varying the number of rules, conditions per rule, and common conditions across rules.

Total test execution time: {total_time:.2f} seconds

## Key Findings

### Fastest Configuration
- File: {fastest['file_name']}
- Rules: {fastest['num_rules']}
- Conditions per rule: {fastest['num_conditions']}
- Common conditions: {fastest['num_common']}
- Average time per rule: {fastest['avg_time']:.4f} ms
- Total execution time: {fastest['total_time']:.4f} ms

### Slowest Configuration
- File: {slowest['file_name']}
- Rules: {slowest['num_rules']}
- Conditions per rule: {slowest['num_conditions']}
- Common conditions: {slowest['num_common']}
- Average time per rule: {slowest['avg_time']:.4f} ms
- Total execution time: {slowest['total_time']:.4f} ms

### Overall Performance
- Average time across all configurations: {overall_avg:.4f} ms
- Performance difference between fastest and slowest: {slowest['avg_time'] / fastest['avg_time']:.2f}x

## Analysis by Rule Count
"""

        # Add analysis for each rule count group
        for rule_count in sorted(rule_groups.keys()):
            group = rule_groups[rule_count]
            group_avg_times = [result['avg_time'] for result in group]
            group_avg = mean(group_avg_times) if group_avg_times else 0

            # Sort by average time
            sorted_group = sorted(group, key=lambda x: x['avg_time'])
            fastest_in_group = sorted_group[0]
            slowest_in_group = sorted_group[-1]

            explanation += f"\n### {rule_count} Rules\n"
            explanation += f"- Average time: {group_avg:.4f} ms\n"
            explanation += f"- Fastest configuration: {fastest_in_group['num_conditions']} conditions, "
            explanation += f"{fastest_in_group['num_common']} common, {fastest_in_group['avg_time']:.4f} ms\n"
            explanation += f"- Slowest configuration: {slowest_in_group['num_conditions']} conditions, "
            explanation += f"{slowest_in_group['num_common']} common, {slowest_in_group['avg_time']:.4f} ms\n"

        # Add conclusions
        explanation += "\n## Conclusions\n\n"

        # Analyze impact of rule count
        if len(rule_groups) > 1:
            avg_by_rule_count = {}
            for rule_count, group in rule_groups.items():
                avg_by_rule_count[rule_count] = mean([r['avg_time'] for r in group])

            min_rule_count = min(avg_by_rule_count.keys())
            max_rule_count = max(avg_by_rule_count.keys())

            scaling_factor = avg_by_rule_count[max_rule_count] / avg_by_rule_count[min_rule_count]
            rule_ratio = max_rule_count / min_rule_count

            explanation += f"1. Scaling from {min_rule_count} to {max_rule_count} rules (a {rule_ratio:.1f}x increase) "
            explanation += f"resulted in a {scaling_factor:.2f}x increase in average processing time.\n"

        # Analyze impact of condition count
        all_condition_counts = set(result['num_conditions'] for result in sorted_results)
        if len(all_condition_counts) > 1:
            explanation += f"\n2. The number of conditions per rule has a significant impact on performance. "
            explanation += f"Rules with more conditions generally take longer to process.\n"

        # Analyze impact of common conditions
        all_common_counts = set(result['num_common'] for result in sorted_results)
        if len(all_common_counts) > 1:
            explanation += f"\n3. Increasing the number of common conditions tends to improve performance, "
            explanation += f"as common conditions can be evaluated once for multiple rules.\n"

        # Add recommendations
        explanation += "\n## Recommendations\n\n"
        explanation += "1. For optimal performance, consider organizing rules to maximize common conditions.\n"
        explanation += "2. When possible, place the most frequently failing conditions early in the rule definition to allow for early termination.\n"
        explanation += "3. For large rule sets, consider breaking them into smaller, more focused groups if appropriate for your use case.\n"

        # Save the explanation to a file in the temp directory
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(temp_dir, f"zato_rule_perf_results_{timestamp}.txt")

        with open(file_path, 'w') as f:
            f.write(explanation)

        print(f"\n{Fore.GREEN}Plain English explanation saved to: {Fore.CYAN}{file_path}{Style.RESET_ALL}")
