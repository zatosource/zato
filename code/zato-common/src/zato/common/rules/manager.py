# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from pathlib import Path

# Zato
from zato.common.rules.cache import CachedRule
from zato.common.rules.evaluation import RuleEvaluator
from zato.common.rules.loader import RuleLoader
from zato.common.rules.models import Container, MatchResult, Rule

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dict_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RulesManager:
    """ Rules manager with condition caching.
    """

    def __init__(self) -> 'None':
        self._all_rules = {}
        self._containers = {}
        self.cached_rules = {}  # type: dict_[str, CachedRule]
        self.evaluator = RuleEvaluator()
        self.loader = RuleLoader()
        self._rules_by_complexity = []  # Rules sorted by complexity

    def __getitem__(self, name:'str') -> 'Rule | Container':
        return getattr(self, name)

    def __getattr__(self, name:'str') -> 'Rule | Container':

        # Check if we have a matching container
        if name in self._containers:

            # .. if yes, return it to the caller ..
            return self._containers[name]

        # .. try to see if we have a rule of that name ..
        elif name in self._all_rules:

            # .. if yes, return that rule ..
            return self._all_rules[name]

        # .. otherwise, give up
        else:
            raise AttributeError(f'No such rule, container or attribute -> {name}')

    def _count_nodes(self, expression) -> 'int':
        """ Count the number of nodes in an expression tree to determine complexity.
        """
        if not hasattr(expression, 'left') or not hasattr(expression, 'right'):
            return 1
        return 1 + self._count_nodes(expression.left) + self._count_nodes(expression.right)

    def _calculate_rule_complexity(self, rule:'Rule') -> 'int':
        """ Calculate the complexity of a rule based on its AST.
        """
        return self._count_nodes(rule.when_impl.statement.expression)

    def _sort_rules_by_complexity(self) -> 'None':
        """ Sort rules by complexity (simplest first) for more efficient evaluation.
        """
        # Create a list of (rule_name, complexity) tuples
        rule_complexity = []
        for rule_name, cached_rule in self.cached_rules.items():
            complexity = self._calculate_rule_complexity(cached_rule.rule)
            rule_complexity.append((rule_name, complexity))
        
        # Sort by complexity (ascending)
        def get_complexity(item):
            """ Get complexity from a (rule_name, complexity) tuple.
            """
            return item[1]
        
        self._rules_by_complexity = sorted(rule_complexity, key=get_complexity)
        logger.info(f'Sorted {len(self._rules_by_complexity)} rules by complexity')

    def match(self, data:'strdict', rules:'any_') -> 'MatchResult | None':
        """ Match data against rules with condition caching.
        """
        # If we have rules sorted by complexity, use them for more efficient matching
        if self._rules_by_complexity and isinstance(rules, list):
            # Filter the sorted rules to only include those in the input list
            rule_set = set(rules)
            sorted_rules = [rule_name for rule_name, _ in self._rules_by_complexity if rule_name in rule_set]
            
            # Use the sorted rules for matching
            return self.evaluator.match(data, sorted_rules, self.cached_rules)
        
        # Otherwise, use the original rules
        return self.evaluator.match(data, rules, self.cached_rules)

    def get_performance_stats(self) -> 'dict_[str, any_]':
        """ Get performance statistics.
        """
        return self.evaluator.get_performance_stats()

    def reset_performance_stats(self) -> 'None':
        """ Reset performance statistics.
        """
        self.evaluator.reset_performance_stats()

    def load_parsed_rules(self, parsed:'strdict', container_name:'str') -> 'strlist':
        """ Load rules from parsed data.
        """
        result = self.loader.load_parsed_rules(parsed, container_name, 
                                             self._all_rules, self._containers, 
                                             self.cached_rules)
        
        # Update common expressions for optimization
        self.evaluator.update_common_expressions(self._all_rules)
        
        # Sort rules by complexity for more efficient evaluation
        self._sort_rules_by_complexity()
        
        return result

    def load_rules_from_file(self, file_path:'str | Path') -> 'strlist':
        """ Load rules from a file.
        """
        result = self.loader.load_rules_from_file(file_path, 
                                               self._all_rules, self._containers, 
                                               self.cached_rules)
        
        # Update common expressions for optimization
        self.evaluator.update_common_expressions(self._all_rules)
        
        # Sort rules by complexity for more efficient evaluation
        self._sort_rules_by_complexity()
        
        return result

    def load_rules_from_directory(self, root_dir:'str | Path') -> 'strlist':
        """ Load rules from a directory.
        """
        result = self.loader.load_rules_from_directory(root_dir, 
                                                    self._all_rules, self._containers, 
                                                    self.cached_rules)
        
        # Update common expressions for optimization
        self.evaluator.update_common_expressions(self._all_rules)
        
        # Sort rules by complexity for more efficient evaluation
        self._sort_rules_by_complexity()
        
        return result

# ################################################################################################################################
# ################################################################################################################################
