# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import time

# Zato
from zato.common.rules.api import RulesManager as BaseRulesManager, MatchResult
from zato.common.rules.rule_cache import CachedRule

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, dict_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RulesManager(BaseRulesManager):
    """ Rules manager with condition caching.
    """

    def __init__(self) -> 'None':
        super().__init__()
        self.cached_rules = {}  # type: dict_[str, CachedRule]
        self.performance_stats = {
            'total_evaluations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0.0
        }  # type: dict_[str, int | float]

    def load_parsed_rules(self, parsed:'strdict', container_name:'str') -> 'strlist':
        """ Override to create cached rules.
        """
        # Call the parent method to load the rules
        rule_names = super().load_parsed_rules(parsed, container_name)

        # Create cached versions of all rules
        with self._lock:
            for rule_name in rule_names:
                rule = self._all_rules[rule_name]
                self.cached_rules[rule_name] = CachedRule(rule)

        return rule_names

    def load_rules_from_file(self, file_path:'str | Path') -> 'strlist':
        """ Override to ensure cached rules are created.
        """
        rule_names = super().load_rules_from_file(file_path)

        # Make sure all rules have cached versions
        with self._lock:
            for rule_name in rule_names:
                if rule_name not in self.cached_rules:
                    rule = self._all_rules[rule_name]
                    self.cached_rules[rule_name] = CachedRule(rule)

        return rule_names

    def match(self, data:'strdict', rules:'any_') -> 'MatchResult | None':
        """ Match data against rules with condition caching.
        """
        # Create a cache for this matching cycle
        condition_cache = {}  # type: dict_[str, any_]

        # Track performance
        start_time = time()

        # Determine which rules to check
        rule_names = [rules] if isinstance(rules, str) else rules

        # Check each rule
        for rule_name in rule_names:
            cached_rule = self.cached_rules.get(rule_name)
            if cached_rule:
                result = cached_rule.match(data, condition_cache)
                if result:
                    # Update performance stats
                    self._update_stats(condition_cache, cached_rule, start_time)
                    return result
            else:
                # Fall back to original rule if cached version not available
                rule = self[rule_name]
                if result := rule.match(data):
                    return result

        # No match found
        self._update_stats(condition_cache, None, start_time)
        return None

    def _update_stats(self, condition_cache:'dict_[str, any_]', cached_rule:'CachedRule | None'=None, start_time:'float'=0) -> 'None':
        """ Update performance statistics.
        """
        self.performance_stats['total_evaluations'] += 1

        if cached_rule:
            self.performance_stats['cache_hits'] += cached_rule.cache_hits
            self.performance_stats['cache_misses'] += cached_rule.cache_misses

        self.performance_stats['total_time'] += time() - start_time

    def get_performance_stats(self) -> 'dict_[str, int | float]':
        """ Get performance statistics.
        """
        stats = self.performance_stats.copy()

        # Calculate derived metrics
        total_conditions = stats['cache_hits'] + stats['cache_misses']
        if total_conditions > 0:
            stats['cache_hit_ratio'] = stats['cache_hits'] / total_conditions
        else:
            stats['cache_hit_ratio'] = 0.0

        if stats['total_evaluations'] > 0:
            stats['avg_evaluation_time'] = stats['total_time'] / stats['total_evaluations']
        else:
            stats['avg_evaluation_time'] = 0.0

        return stats

    def reset_performance_stats(self) -> 'None':
        """ Reset performance statistics.
        """
        self.performance_stats = {
            'total_evaluations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0.0
        }

# ################################################################################################################################
# ################################################################################################################################
