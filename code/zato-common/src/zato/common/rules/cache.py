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
from zato.common.rules.models import MatchResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, bool_, dict_, strdict
    from zato.common.rules.models import Rule

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

    def _get_cache_key(self, expression:'ExpressionBase') -> 'str':
        """ Generate an optimized cache key for expressions.
        """
        # For LogicExpression, use a more efficient key format
        if isinstance(expression, LogicExpression):
            left_key = str(expression.left)[:50]  # Limit length for efficiency
            right_key = str(expression.right)[:50]  # Limit length for efficiency
            return f'{expression.type}:{left_key}:{right_key}'

        # For other expressions, use the string representation
        return str(expression)

    def _evaluate_with_cache(self, expression:'ExpressionBase', data:'anydict', cache:'dict_[str, any_]') -> 'bool_':
        """ Evaluate an expression with caching.
        """
        # Generate a cache key based on the expression
        cache_key = self._get_cache_key(expression)

        # Check if result is already in cache
        if cache_key in cache:
            self.cache_hits += 1
            return cache[cache_key]

        self.cache_misses += 1

        # Fast path for non-logical expressions
        if not isinstance(expression, LogicExpression):
            try:
                result = expression.evaluate(data)
                cache[cache_key] = result
                return bool(result)
            except Exception as e:
                logger.warning(f'Error evaluating expression {cache_key}: {e}')
                return False

        # For LogicExpression, handle specially to maintain short-circuit evaluation
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

        # For other types of expressions, evaluate directly
        try:
            result = expression.evaluate(data)
            cache[cache_key] = result
            return bool(result)
        except Exception as e:
            logger.warning(f'Error evaluating expression {cache_key}: {e}')
            return False

# ################################################################################################################################
# ################################################################################################################################

def identify_common_expressions(rules:'dict_[str, Rule]') -> 'list[str]':
    """ Identify common expressions across all rules.
    """
    expression_count = {}

    for rule in rules.values():
        # Extract expressions from the rule
        expressions = _extract_expressions(rule.when_impl.statement.expression)

        # Count occurrences of each expression
        for expr in expressions:
            expr_str = str(expr)
            expression_count[expr_str] = expression_count.get(expr_str, 0) + 1

    # Return the most common expressions (those that appear in multiple rules)
    result = []
    
    # Sort expressions by frequency (most common first)
    sorted_expressions = sorted(expression_count.items(), key=lambda x: x[1], reverse=True)
    
    # Add expressions that appear in multiple rules to the result
    for expr, count in sorted_expressions:
        if count > 1:
            result.append(expr)
    
    return result

def _extract_expressions(expression:'ExpressionBase') -> 'list[ExpressionBase]':
    """ Extract all subexpressions from an expression tree.
    """
    result = [expression]

    # If this is a compound expression, also extract its components
    if hasattr(expression, 'left') and hasattr(expression, 'right'):
        result.extend(_extract_expressions(expression.left))
        result.extend(_extract_expressions(expression.right))

    return result

def precompute_common_expressions(common_expressions:'list[str]', data:'anydict',  cache:'dict_[str, any_]') -> 'None':
    """ Precompute results for common expressions.
    """
    # This is a placeholder - in a real implementation, we would need to
    # convert the expression strings back to expression objects
    pass

# ################################################################################################################################
# ################################################################################################################################
