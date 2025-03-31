# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from pathlib import Path

# Zato
from zato.common.rules.perf_utils import RulePerformanceTester

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Run the performance tests for 10-rule files and display the results. """
    print(f'Starting performance tests at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Get the directory where the test files are located
    test_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Create the performance tester for 10-rule files
    tester = RulePerformanceTester(rules_dir=test_dir, pattern='perf_010_*.zrules')
    
    # Run the tests with 3 iterations and 1000 runs per iteration for reliable results
    tester.run_tests(iterations=3, runs_per_iteration=1000)
    
    # Display the results in an ASCII table
    tester.display_results()
    
    print(f'Completed performance tests at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
