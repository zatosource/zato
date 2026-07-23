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
from zato.common.rules.cache import build_expression_key
from zato.common.rules.document import resolve_actions
from zato.common.rules.errors import build_evaluation_error

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dict_

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

        # Content-based cache keys per expression node, computed once because the
        # expression tree is immutable for as long as the rule is loaded.
        self._expression_keys = {}  # type: dict_[int, str]

    def match(self, data:'anydict', condition_cache:'dict_[str, any_] | None'=None) -> 'MatchResult':
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

        # Evaluate with caching, turning a missing value or a type mismatch
        # into a loud readable error instead of a silent non-match.
        if condition_cache is not None:
            result = self._evaluate_with_cache(self.rule.when_impl.statement.expression, data, condition_cache)
        else:
            try:
                result = self.rule.when_impl.matches(data)
            except Exception as e:
                raise build_evaluation_error(self.name, e) from e

        # Build a match result object
        match_result = MatchResult(result)
        match_result.full_name = self.rule.full_name

        # A match applies the then actions and a non-match still applies the else actions,
        # with an unresolvable reference turned into a loud readable error either way.
        try:
            if result:
                match_result.then = resolve_actions(self.rule.then, data)
            else:
                match_result.else_ = resolve_actions(self.rule.else_, data)
        except Exception as e:
            raise build_evaluation_error(self.name, e) from e

        return match_result

    def _evaluate_with_cache(self, expression:'ExpressionBase', data:'anydict', cache:'dict_[str, any_]') -> 'bool':
        """ Evaluate an expression with caching.
        """
        # Generate a content-based cache key for the expression, computed at most once per node -
        # the str() of an expression names only its type and would collide across conditions.
        cache_key = self._expression_keys.get(id(expression))
        if cache_key is None:
            cache_key = build_expression_key(expression)
            self._expression_keys[id(expression)] = cache_key

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
            # A value that cannot be evaluated is a loud readable error, never a silent non-match.
            raise build_evaluation_error(self.name, e) from e

# ################################################################################################################################
# ################################################################################################################################
