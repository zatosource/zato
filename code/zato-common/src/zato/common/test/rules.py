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
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RuleTestHelper:
    """ Helper class for rule testing that handles rule file renaming and provides common functionality.
    """

    def __init__(self, rules_dir=None) -> 'None':
        # Get the directory where the test files are located
        if rules_dir:
            self.current_dir = rules_dir
        else:
            # Default to the current directory where this helper is located
            self.current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

        # Create a rules manager
        self.rules_manager = RulesManager()

        # Load all the rules files
        _ = self.rules_manager.load_rules_from_directory(self.current_dir)

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
