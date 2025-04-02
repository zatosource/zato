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
from typing import Any, Dict, List

# Zato
from zato.common.rules.api import RulesManager
from zato.common.rules.parser import parse_file

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestRulesParser(unittest.TestCase):

    def test_parser(self):
        """ Tests loading and parsing all .zrules files in the rules directory.
        """
        # Get the current directory where the test files are located
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

        # Check for zrules subdirectory
        zrules_dir = current_dir / 'zrules'
        if zrules_dir.exists() and zrules_dir.is_dir():
            # Find all .zrules files in the zrules subdirectory
            all_zrules_files = list(zrules_dir.glob('*.zrules'))
            # Filter out performance test files
            zrules_files = [f for f in all_zrules_files if not f.name.startswith('perf_')]
            logger.info(f'Looking for .zrules files in the zrules subdirectory: {zrules_dir}')
            logger.info(f'Found {len(all_zrules_files)} total files, using {len(zrules_files)} non-performance files')
        else:
            # Find all .zrules files in the current directory (fallback)
            all_zrules_files = list(current_dir.glob('*.zrules'))
            # Filter out performance test files
            zrules_files = [f for f in all_zrules_files if not f.name.startswith('perf_')]
            logger.info(f'Looking for .zrules files in the current directory: {current_dir}')
            logger.info(f'Found {len(all_zrules_files)} total files, using {len(zrules_files)} non-performance files')

        # Ensure we found some rule files
        self.assertTrue(zrules_files, 'No .zrules files found in the test directory or zrules subdirectory')

        # Create a rules manager
        rules_manager = RulesManager()

        # Load all the rules files
        loaded_rules: List[str] = []

        for zrules_file in zrules_files:
            # Get the container name from the file name (without .zrules extension)
            container_name = zrules_file.stem

            logger.info(f'Processing file: {zrules_file}, container: {container_name}')

            # Parse the file
            parsed_rules: List[Dict[str, Any]] = parse_file(zrules_file, container_name)

            # Check that we got some rules
            self.assertTrue(parsed_rules, f'No rules parsed from {zrules_file}')

            # Load the parsed rules into the rules manager
            rule_names: List[str] = rules_manager.load_parsed_rules(parsed_rules, container_name)

            # Check that we loaded some rules
            self.assertTrue(rule_names, f'No rules loaded from {zrules_file}')

            # Add to our list of loaded rules
            loaded_rules.extend(rule_names)

        # Verify that we loaded all the expected rules
        self.assertTrue(loaded_rules, 'No rules were loaded')
        logger.info(f'Successfully loaded {len(loaded_rules)} rules')

        # Test that we can access the rules through the manager
        for rule_name in loaded_rules:
            # The rule should be accessible directly by its full name
            rule = rules_manager[rule_name]

            # Check that the rule has the expected attributes
            self.assertEqual(rule.full_name, rule_name, f'Rule {rule_name} has incorrect full_name')
            self.assertTrue(hasattr(rule, 'when') and rule.when, f'Rule {rule_name} is missing when condition')
            self.assertTrue(hasattr(rule, 'when_impl'), f'Rule {rule_name} is missing when_impl')

            # Get the container name from the rule's container_name attribute
            container_name = rule.container_name

            # Check if the container exists
            self.assertIn(container_name, rules_manager._containers,
                         f'Container {container_name} not found in rules_manager')

            # Get the container
            container = rules_manager._containers[container_name] # type: ignore

            # Check if the rule is in the container
            self.assertIn(rule.full_name, container._rules,
                         f'Rule {rule.full_name} not found in container {container_name}')

            # Get the rule from the container
            container_rule = container._rules[rule.full_name] # type: ignore

            # Verify the rule is the same
            self.assertEqual(container_rule.full_name, rule_name,
                            f'Container rule {container_rule.full_name} does not match {rule_name}')

        logger.info('Test completed successfully')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
