# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from pathlib import Path

# Zato
from zato.common.rules.api import RulesManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dict_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RuleTestHelper:
    """ Helper class for rule testing that handles rule file renaming and provides common functionality.
    """

    def __init__(self, rules_dir=None, include_perf_files=False) -> 'None':
        # Get the directory where the test files are located
        if rules_dir:
            self.current_dir = rules_dir
        else:
            # Default to the current directory where this helper is located
            self.current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

        # Flag to determine if performance test files should be included
        self.include_perf_files = include_perf_files

        # Create a rules manager
        self.rules_manager = RulesManager()

        # Check if there's a zrules subdirectory
        zrules_dir = self.current_dir / 'zrules'
        if zrules_dir.exists() and zrules_dir.is_dir():
            load_dir = zrules_dir
            logger.info(f'Loading rules from zrules subdirectory: {load_dir}')
            
            # Load rule files based on the include_perf_files flag
            self._load_rules(load_dir)
        else:
            load_dir = self.current_dir
            logger.info(f'Loading rules from current directory: {load_dir}')
            
            # Load rule files based on the include_perf_files flag
            self._load_rules(load_dir)

        # Ensure we have loaded the test rules
        if not self.rules_manager._all_rules:
            raise ValueError('No rules were loaded')

        # Log the loaded rules for debugging
        logger.info(f'Loaded rules: {list(self.rules_manager._all_rules.keys())}')

        # Cache rule conditions for quick lookup
        self.rule_conditions = {}
        for rule_name, rule in self.rules_manager._all_rules.items():
            self.rule_conditions[rule_name] = rule.when
            logger.info(f'Rule {rule_name} conditions: {rule.when}')
            
    def _load_rules(self, directory:'Path') -> 'None':
        """Load rule files from the directory, optionally including performance test files."""
        # Find all .zrules files in the directory
        all_files = list(directory.glob('*.zrules'))
        
        # Check if there's a perf subdirectory
        perf_dir = directory / 'perf'
        perf_files = []
        
        if perf_dir.exists() and perf_dir.is_dir() and self.include_perf_files:
            # Find all .zrules files in the perf subdirectory
            perf_files = list(perf_dir.glob('*.zrules'))
            logger.info(f'Found {len(perf_files)} performance test files in {perf_dir}')
        
        # Filter out performance test files from the main directory
        non_perf_files = [f for f in all_files if not f.name.startswith('perf_')]
        
        if self.include_perf_files:
            # Include all files from the main directory and perf subdirectory
            files_to_load = non_perf_files + perf_files
            logger.info(f'Loading {len(non_perf_files)} regular files and {len(perf_files)} performance files')
        else:
            # Only include non-performance files from the main directory
            files_to_load = non_perf_files
            logger.info(f'Loading {len(non_perf_files)} regular files (excluding performance files)')
        
        # Load each file individually
        for rule_file in files_to_load:
            self.rules_manager.load_rules_from_file(rule_file)

    def find_rules_with_condition(self, condition_text:'str') -> 'strlist':
        """ Find rules that contain the specified text in their condition.
            Returns a list of rule names.
        """
        matching_rules = []
        for rule_name, condition in self.rule_conditions.items():
            if condition_text in condition:
                matching_rules.append(rule_name)
        return matching_rules

    def find_rules_with_all_conditions(self, condition_texts:'strlist') -> 'strlist':
        """ Find rules that contain all the specified texts in their condition.
            Returns a list of rule names.
        """
        matching_rules = []
        for rule_name, condition in self.rule_conditions.items():
            all_match = True
            for text in condition_texts:
                if text not in condition:
                    all_match = False
                    break
            if all_match:
                matching_rules.append(rule_name)
        return matching_rules

    def find_rules_without_conditions(self, condition_texts:'strlist') -> 'strlist':
        """ Find rules that don't contain any of the specified texts in their condition.
            Returns a list of rule names.
        """
        matching_rules = []
        for rule_name, condition in self.rule_conditions.items():
            none_match = True
            for text in condition_texts:
                if text in condition:
                    none_match = False
                    break
            if none_match:
                matching_rules.append(rule_name)
        return matching_rules

    def find_rules_with_condition_and_without_others(self, include_text:'str', exclude_texts:'strlist') -> 'strlist':
        """ Find rules that contain the include_text but none of the exclude_texts.
            Returns a list of rule names.
        """
        matching_rules = []
        for rule_name, condition in self.rule_conditions.items():
            if include_text in condition:
                exclude_match = False
                for text in exclude_texts:
                    if text in condition:
                        exclude_match = True
                        break
                if not exclude_match:
                    matching_rules.append(rule_name)
        return matching_rules

    def find_rules_with_parentheses(self) -> 'strlist':
        """ Find rules that contain parentheses in their condition.
            Returns a list of rule names.
        """
        matching_rules = []
        for rule_name, condition in self.rule_conditions.items():
            if '(' in condition and ')' in condition:
                matching_rules.append(rule_name)
        return matching_rules

    def find_simple_equality_rules(self) -> 'strlist':
        """ Find rules with simple equality conditions (x == y).
            Returns a list of rule names.
        """
        matching_rules = []
        for rule_name, condition in self.rule_conditions.items():
            if ' == ' in condition and ' and ' not in condition and ' or ' not in condition:
                matching_rules.append(rule_name)
        return matching_rules

    def find_rule_by_pattern(self, pattern:'str') -> 'str':
        """ Find a rule that matches a specific pattern in its condition.
            Returns the first matching rule name or None.
        """
        for rule_name, condition in self.rule_conditions.items():
            if pattern in condition:
                return rule_name
        return None

    def get_rule_condition(self, rule_name:'str') -> 'str':
        """ Get the condition for a specific rule.
        """
        return self.rule_conditions.get(rule_name)

    def match_rule(self, rule_name:'str', data:'anydict') -> 'any_':
        """ Match data against a specific rule.
        """
        return self.rules_manager[rule_name].match(data)

# ################################################################################################################################
# ################################################################################################################################
