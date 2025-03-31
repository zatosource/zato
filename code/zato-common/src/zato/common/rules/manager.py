# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from pathlib import Path

# Zato
from zato.common.rules.cache import CachedRule, build_field_index
from zato.common.rules.evaluation import RuleEvaluator
from zato.common.rules.loader import RuleLoader
from zato.common.rules.models import Container, MatchResult, Rule

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dict_, set_, strdict, strlist

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
        self._field_to_rules = {}  # Index of rules by field access

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

    def _build_field_index(self) -> 'None':
        """ Build an index of rules by the fields they access.
        """
        self._field_to_rules = build_field_index(self._all_rules)
        logger.info(f'Built field index with {len(self._field_to_rules)} fields')

    def _filter_rules_by_fields(self, rules:'list[str]', data:'strdict') -> 'list[str]':
        """ Filter rules to only include those that access fields present in the data.
        """
        if not self._field_to_rules:  # If field index is empty, return all rules
            return rules

        # Get the fields present in the data
        data_fields = set(data.keys())

        # Find rules that only access fields present in the data
        candidate_rules = set()

        # For each field in the data, add all rules that access it
        for field in data_fields:
            if field in self._field_to_rules:
                candidate_rules.update(self._field_to_rules[field])

        # Intersect with the requested rules
        rules_set = set(rules)
        filtered_rules = list(candidate_rules.intersection(rules_set))

        # If no rules match the field criteria, fall back to all requested rules
        # This handles cases where rules might not access any fields directly
        if not filtered_rules:
            return rules

        # Log how many rules we're skipping
        skipped = len(rules) - len(filtered_rules)
        if skipped > 0:
            logger.debug(f'Field indexing skipped {skipped} rules out of {len(rules)}')

        return filtered_rules

    def match(self, data:'strdict', rules:'any_') -> 'MatchResult | None':
        """ Match data against rules with condition caching.
        """
        # Convert single rule to list
        rule_names = [rules] if isinstance(rules, str) else rules

        # Filter rules by fields they access
        filtered_rules = self._filter_rules_by_fields(rule_names, data)

        # If we have rules sorted by complexity, use the sort order
        if self._rules_by_complexity and len(filtered_rules) > 1:
            # Create a mapping of rule name to complexity rank
            complexity_rank = {name: idx for idx, (name, _) in enumerate(self._rules_by_complexity)}

            # Sort the filtered rules by complexity
            def get_complexity_rank(rule_name):
                return complexity_rank.get(rule_name, float('inf'))

            sorted_rules = sorted(filtered_rules, key=get_complexity_rank)

            # Use the sorted rules for matching
            return self.evaluator.match(data, sorted_rules, self.cached_rules)

        # Otherwise, use the filtered rules as is
        return self.evaluator.match(data, filtered_rules, self.cached_rules)

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
        result = self.loader.load_parsed_rules(
            parsed, container_name, self._all_rules, self._containers, self.cached_rules
        )

        # Update common expressions for optimization
        self.evaluator.update_common_expressions(self._all_rules)

        # Sort rules by complexity for more efficient evaluation
        self._sort_rules_by_complexity()

        # Build field index for more efficient rule filtering
        self._build_field_index()

        return result

    def load_rules_from_file(self, file_path:'str | Path') -> 'strlist':
        """ Load rules from a file.
        """
        result = self.loader.load_rules_from_file(
            file_path, self._all_rules, self._containers, self.cached_rules
        )

        # Update common expressions for optimization
        self.evaluator.update_common_expressions(self._all_rules)

        # Sort rules by complexity for more efficient evaluation
        self._sort_rules_by_complexity()

        # Build field index for more efficient rule filtering
        self._build_field_index()

        return result

    def load_rules_from_directory(self, root_dir:'str | Path') -> 'strlist':
        """ Load rules from a directory.
        """
        result = self.loader.load_rules_from_directory(
            root_dir, self._all_rules, self._containers, self.cached_rules
        )

        # Update common expressions for optimization
        self.evaluator.update_common_expressions(self._all_rules)

        # Sort rules by complexity for more efficient evaluation
        self._sort_rules_by_complexity()

        # Build field index for more efficient rule filtering
        self._build_field_index()

        return result

# ################################################################################################################################
# ################################################################################################################################
