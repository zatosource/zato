# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
import time
from datetime import datetime
from statistics import mean

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

def _by_avg_time(result:'anydict') -> 'float':
    return result['avg_time']

def _by_total_time(result:'anydict') -> 'float':
    return result['total_time']

def _by_conditions_and_common(result:'anydict') -> 'anytuple':
    return (result['num_conditions'], result['num_common'])

def _by_rules_conditions_common(result:'anydict') -> 'anytuple':
    return (result['num_rules'], result['num_conditions'], result['num_common'])

def _by_second_item(item:'anytuple') -> 'any_':
    return item[1]

# Add colorama for terminal colors
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # Create dummy classes if colorama is not available
    class DummyFore:
        def __getattr__(self, name:'str') -> 'str':
            return ''
    class DummyStyle:
        def __getattr__(self, name:'str') -> 'str':
            return ''
    Fore = DummyFore()
    Style = DummyStyle()

# ################################################################################################################################
# ################################################################################################################################

class ASCIITable:
    """ Simple ASCII table generator without external dependencies. """

    @staticmethod
    def make_table(data:'anylist', headers:'strlist') -> 'str':
        """ Create an ASCII table with the given data and headers. """
        if not data:
            return "No data available"

        # Convert all data to strings
        str_data = []
        for row in data:
            str_row = []
            for cell in row:
                str_row.append(str(cell))
            str_data.append(str_row)

        # Calculate column widths - each column is at least as wide as its header
        col_widths = []
        for index, header in enumerate(headers):
            width = len(header)
            for row in str_data:
                cell_length = len(row[index])
                if cell_length > width:
                    width = cell_length
            col_widths.append(width)

        # Create the header row
        header_cells = []
        for header, width in zip(headers, col_widths):
            header_cells.append(header.ljust(width))
        header_row = '| ' + ' | '.join(header_cells) + ' |'

        separator_parts = []
        for width in col_widths:
            separator_parts.append('-' * (width + 2))
        separator = '+' + '+'.join(separator_parts) + '+'
        separator = separator.replace('+-+', '---')

        # Create the data rows
        data_rows = []
        for row in str_data:
            row_cells = []
            for cell, width in zip(row, col_widths):
                row_cells.append(cell.ljust(width))
            data_rows.append('| ' + ' | '.join(row_cells) + ' |')

        # Combine all parts
        table = [separator, header_row, separator] + data_rows + [separator]

        return '\n'.join(table)

class BarChart:
    """ Simple ASCII bar chart generator without external dependencies. """

    @staticmethod
    def render(data:'anylist', title:'str'='', xlabel:'str'='', ylabel:'str'='', width:'int'=60, height:'int'=10) -> 'str':
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
        max_label_length = 0
        for label in labels:
            if len(label) > max_label_length:
                max_label_length = len(label)

        # Create the bars
        for label, value in data:
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

class PerfDisplay:
    """ The presentation side of the performance tester - tables, charts and the plain-text summary.
    The attributes below are filled in by the tester that mixes this class in.
    """
    results:'anylist'
    rule_groups:'anydict'
    group_times:'anydict'
    total_start_time:'float'

    def _chart_data(self, results:'dictlist') -> 'anytuple':
        """ Builds the (label, value) pairs for the side-by-side average and total time charts. """
        avg_chart_data = []
        for result in sorted(results, key=_by_avg_time):
            label = f"{result['num_rules']:003d} rules, {result['num_conditions']:003d} cond, {result['num_common']:003d} common"
            avg_chart_data.append((label, result['avg_time']))

        total_chart_data = []
        for result in sorted(results, key=_by_total_time):
            label = f"{result['num_rules']:003d} rules, {result['num_conditions']:003d} cond, {result['num_common']:003d} common"
            total_chart_data.append((label, result['total_time']))

        return avg_chart_data, total_chart_data

    def _print_side_by_side_charts(self, results:'dictlist') -> 'None':
        """ Prints the average and total time bar charts next to each other. """
        avg_chart_data, total_chart_data = self._chart_data(results)

        # Find the maximum label length for alignment
        max_label_length = 0
        for label, _ in avg_chart_data:
            if len(label) > max_label_length:
                max_label_length = len(label)

        # Calculate scaling factors for the bars
        max_avg_value = 0.0
        for _, value in avg_chart_data:
            if value > max_avg_value:
                max_avg_value = value

        max_total_value = 0.0
        for _, value in total_chart_data:
            if value > max_total_value:
                max_total_value = value

        avg_scale = 30 / max_avg_value if max_avg_value > 0 else 0
        total_scale = 30 / max_total_value if max_total_value > 0 else 0

        # Define fixed column widths
        avg_column_width = 80  # Width for the average time column

        # Print headers for the charts
        print(f"\n{Fore.CYAN}Average Time per Rule (ms){' ' * (avg_column_width - 25)}{Fore.CYAN}Total File Execution Time (ms){Style.RESET_ALL}")
        print(f"{'-' * avg_column_width}{'-' * 50}")

        # Print the bars side by side with fixed column widths
        for (avg_label, avg_value), (total_label, total_value) in zip(
            sorted(avg_chart_data, key=_by_second_item),
            sorted(total_chart_data, key=_by_second_item)
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

    def _display_group_results(self, rule_count:'int') -> 'None':
        """ Display results for a specific rule count group. """
        if rule_count not in self.rule_groups:
            return

        if not self.rule_groups[rule_count]:
            return

        print(f"\n{Fore.CYAN}{'=' * 30} Performance Results for {rule_count} Rules {'=' * 30}{Style.RESET_ALL}")

        # Sort results by common conditions
        sorted_results = sorted(self.rule_groups[rule_count], key=_by_conditions_and_common)

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
        self._print_side_by_side_charts(sorted_results)

        # Display group timing information
        if rule_count in self.group_times:
            duration = self.group_times[rule_count]
            print(f"\n{Fore.YELLOW}Group test time: {Fore.CYAN}{duration:.2f} seconds{Style.RESET_ALL}")

    def display_results(self) -> 'None':
        """ Display the performance test results in an ASCII table. """
        if not self.results:
            print(f"{Fore.RED}No results to display. Run tests first.{Style.RESET_ALL}")
            return

        # Sort results by rule count, then conditions, then common conditions
        sorted_results = sorted(self.results, key=_by_rules_conditions_common)

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
        self._print_side_by_side_charts(sorted_results)

        # Add total time information
        total_time = time.time() - self.total_start_time
        print(f"\n{Fore.YELLOW}Total test time: {Fore.CYAN}{total_time:.2f} seconds{Style.RESET_ALL}")

        # Generate a plain English explanation and save to a file in the temp directory
        self._save_plain_text_summary(sorted_results, total_time)

    def _save_plain_text_summary(self, sorted_results:'dictlist', total_time:'float') -> 'None':
        """ Generate a plain English explanation of the test results and save to a file. """
        # Get the fastest and slowest configurations
        by_avg_time = sorted(sorted_results, key=_by_avg_time)
        fastest = by_avg_time[0]
        slowest = by_avg_time[-1]

        # Get the average time across all tests
        all_avg_times = []
        for result in sorted_results:
            all_avg_times.append(result['avg_time'])
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

            group_avg_times = []
            for result in group:
                group_avg_times.append(result['avg_time'])
            group_avg = mean(group_avg_times) if group_avg_times else 0

            # Sort by average time
            sorted_group = sorted(group, key=_by_avg_time)
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
                averages = []
                for result in group:
                    averages.append(result['avg_time'])
                avg_by_rule_count[rule_count] = mean(averages)

            min_rule_count = min(avg_by_rule_count.keys())
            max_rule_count = max(avg_by_rule_count.keys())

            scaling_factor = avg_by_rule_count[max_rule_count] / avg_by_rule_count[min_rule_count]
            rule_ratio = max_rule_count / min_rule_count

            explanation += f"1. Scaling from {min_rule_count} to {max_rule_count} rules (a {rule_ratio:.1f}x increase) "
            explanation += f"resulted in a {scaling_factor:.2f}x increase in average processing time.\n"

        # Analyze impact of condition count
        all_condition_counts = set()
        for result in sorted_results:
            all_condition_counts.add(result['num_conditions'])
        if len(all_condition_counts) > 1:
            explanation += "\n2. The number of conditions per rule has a significant impact on performance. "
            explanation += "Rules with more conditions generally take longer to process.\n"

        # Analyze impact of common conditions
        all_common_counts = set()
        for result in sorted_results:
            all_common_counts.add(result['num_common'])
        if len(all_common_counts) > 1:
            explanation += "\n3. Increasing the number of common conditions tends to improve performance, "
            explanation += "as common conditions can be evaluated once for multiple rules.\n"

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
            _ = f.write(explanation)

        print(f"\n{Fore.GREEN}Plain English explanation saved to: {Fore.CYAN}{file_path}{Style.RESET_ALL}")

# ################################################################################################################################
# ################################################################################################################################
