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

def main() -> 'None':
    """ Run the performance tests for rule files and display the results. """
    parser = argparse.ArgumentParser(description='Run performance tests for Zato rule engine')
    parser.add_argument('--pattern', type=str, default=None, help='Pattern to match rule files (e.g., "perf_010_*.zrules")')
    parser.add_argument('--iterations', type=int, default=3, help='Number of iterations to run for each test')
    parser.add_argument('--runs', type=int, default=1000, help='Number of runs per iteration')
    args = parser.parse_args()
    
    print(f'Starting performance tests at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Get the directory where the test files are located
    test_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Create the performance tester with the specified pattern or all files
    tester = RulePerformanceTester(rules_dir=test_dir, pattern=args.pattern)
    
    # Run the tests with the specified iterations and runs per iteration
    tester.run_tests(iterations=args.iterations, runs_per_iteration=args.runs)
    
    # Display the results in an ASCII table
    tester.display_results()
    
    print(f'Completed performance tests at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
