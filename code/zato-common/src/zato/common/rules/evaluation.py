# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import time

# Zato
from zato.common.rules.cache import CachedRule, identify_common_expressions, precompute_common_expressions

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dict_, float_, strdict
    from zato.common.rules.models import MatchResult

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RuleEvaluator:
    """ Handles the evaluation of rules against data with optimized caching.
    """
    
    def __init__(self):
        self.performance_stats = {
            'total_evaluations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0.0
        }  # type: dict_[str, int | float_]
        self.common_expressions = []
    
    def match(self, data:'strdict', rule_names:'any_', cached_rules:'dict_[str, CachedRule]') -> 'MatchResult | None':
        """ Match data against rules with condition caching.
        """
        # Create a cache for this matching cycle
        condition_cache = {}  # type: dict_[str, any_]
        
        # Track performance
        start_time = time()
        
        # Precompute common conditions if we have identified them
        if self.common_expressions:
            precompute_common_expressions(self.common_expressions, data, condition_cache)
        
        # Determine which rules to check
        rule_names_list = [rule_names] if isinstance(rule_names, str) else rule_names
        
        # Check each rule
        for rule_name in rule_names_list:
            cached_rule = cached_rules.get(rule_name)
            if cached_rule:
                result = cached_rule.match(data, condition_cache)
                if result:
                    # Update performance stats
                    self._update_stats(condition_cache, cached_rule, start_time)
                    return result
        
        # No match found
        self._update_stats(condition_cache, None, start_time)
        return None
    
    def _update_stats(self, condition_cache:'dict_[str, any_]', cached_rule:'CachedRule | None'=None, start_time:'float_'=0) -> 'None':
        """ Update performance statistics.
        """
        self.performance_stats['total_evaluations'] += 1
        
        if cached_rule:
            self.performance_stats['cache_hits'] += cached_rule.cache_hits
            self.performance_stats['cache_misses'] += cached_rule.cache_misses
        
        self.performance_stats['total_time'] += time() - start_time
    
    def get_performance_stats(self) -> 'dict_[str, int | float_]':
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
    
    def update_common_expressions(self, rules:'dict_[str, any_]') -> 'None':
        """ Update the list of common expressions based on the current rules.
        """
        self.common_expressions = identify_common_expressions(rules)

# ################################################################################################################################
# ################################################################################################################################
