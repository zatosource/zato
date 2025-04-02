# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from logging import getLogger

# rule-engine
from rule_engine.ast import ExpressionBase, LogicExpression

# Zato
from zato.common.rules.api import MatchResult, Rule

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from rule_engine.ast import ExpressionBase
    from zato.common.typing_ import any_, anydict, bool_, dict_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CachedRule:
    """ A wrapper around Zato's Rule class that adds condition caching.
    """

    def __init__(self, rule:'Rule') -> 'None':
        self.rule = rule
        self.name = rule.full_name
        self.cache_hits = 0
        self.cache_misses = 0

    def match(self, data:'anydict', condition_cache:'dict_[str, any_]'=None) -> 'MatchResult':
        """ Match data against the rule using condition caching.
        """
        # Reset statistics for this evaluation
        self.cache_hits = 0
        self.cache_misses = 0

        # Apply default values if needed
        if self.rule.defaults:
            needs_defaults = False
            for key in self.rule.defaults:
                if key not in data:
                    needs_defaults = True
                    break

            if needs_defaults:
                data = deepcopy(data)
                for key, value in self.rule.defaults.items():
                    if key not in data:
                        data[key] = value

        # Evaluate with caching
        if condition_cache is not None:
            result = self._evaluate_with_cache(self.rule.when_impl.statement.expression, data, condition_cache)
        else:
            result = self.rule.when_impl.matches(data)

        # Build a match result object
        match_result = MatchResult(result)
        if result:
            match_result.then = self.rule.then
            match_result.full_name = self.rule.full_name

        return match_result

    def _evaluate_with_cache(self, expression:'ExpressionBase', data:'anydict', cache:'dict_[str, any_]') -> 'bool_':
        """ Evaluate an expression with caching.
        """
        # Generate a cache key based on the expression
        cache_key = str(expression)

        # Check if result is already in cache
        if cache_key in cache:
            self.cache_hits += 1
            return cache[cache_key]

        self.cache_misses += 1

        # For LogicExpression, handle specially to maintain short-circuit evaluation
        if isinstance(expression, LogicExpression):
            if expression.type == 'and':
                # For AND, evaluate left side first
                left_result = self._evaluate_with_cache(expression.left, data, cache)
                if not left_result:
                    # Short-circuit: left is False, so AND is False
                    cache[cache_key] = False
                    return False

                # Left is True, evaluate right side
                right_result = self._evaluate_with_cache(expression.right, data, cache)
                result = bool(right_result)
                cache[cache_key] = result
                return result

            elif expression.type == 'or':
                # For OR, evaluate left side first
                left_result = self._evaluate_with_cache(expression.left, data, cache)
                if left_result:
                    # Short-circuit: left is True, so OR is True
                    cache[cache_key] = True
                    return True

                # Left is False, evaluate right side
                right_result = self._evaluate_with_cache(expression.right, data, cache)
                result = bool(right_result)
                cache[cache_key] = result
                return result

        # For other expressions, evaluate directly
        try:
            result = expression.evaluate(data)
            cache[cache_key] = result
            return bool(result)
        except Exception as e:
            logger.warning(f'Error evaluating expression {cache_key}: {e}')
            return False

# ################################################################################################################################
# ################################################################################################################################
