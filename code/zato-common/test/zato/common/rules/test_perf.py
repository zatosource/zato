#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import os
from datetime import datetime
from pathlib import Path

# Zato
from zato.common.rules.perf_utils import RulePerformanceTester

# ################################################################################################################################
# ################################################################################################################################

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run performance tests for the rule engine')
    _ = parser.add_argument('--pattern', type=str, default=None, help='Pattern to match rule files (e.g., "perf_010_*.zrules")')
    _ = parser.add_argument('--iterations', type=int, default=3, help='Number of iterations to run for each test')
    _ = parser.add_argument('--runs', type=int, default=1000, help='Number of runs per iteration')
    _ = parser.add_argument('rule_counts', nargs='*', type=int, help='Specific rule counts to test (e.g., 10 30 100)')
    args = parser.parse_args()

    print(f'Starting performance tests at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # Get the test directory
    test_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    # Create the performance tester with the specified pattern or all files
    tester = RulePerformanceTester(rules_dir=test_dir, pattern=args.pattern)

    # If specific rule counts were provided, filter the files to only include those rule counts
    if args.rule_counts:
        rule_counts = args.rule_counts
        if rule_counts:
            print(f"Testing only rule files with rule counts: {', '.join(str(count) for count in rule_counts)}")
            tester.filter_by_rule_counts(rule_counts)
        else:
            print("No valid rule counts provided. Testing all rule files.")

    # Run the tests with the specified iterations and runs per iteration
    tester.run_tests(iterations=args.iterations, runs_per_iteration=args.runs)

    # Display the results in an ASCII table
    tester.display_results()

    print(f'Completed performance tests at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
