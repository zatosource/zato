# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# rule-engine
from rule_engine.ast import ExpressionBase, LogicExpression

# Zato
from zato.common.rule_engine.document import resolve_actions
from zato.common.rule_engine.errors import build_evaluation_error
from zato.common.rule_engine.models import MatchResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dict_
    from zato.common.rule_engine.models import Rule

# ################################################################################################################################
# ################################################################################################################################

def build_expression_key(expression:'any_') -> 'str':
    """ Builds a content-based cache key for an expression tree.

    The str() of a rule-engine AST node names only its type, so two different conditions
    would collide under it and one rule's cached result would poison another rule's evaluation.
    This key serializes the whole tree instead - type, attributes and literal values.
    """

    # Lists and tuples serialize element by element ..
    if isinstance(expression, (list, tuple)):
        parts = []
        for item in expression:
            child_key = build_expression_key(item)
            parts.append(child_key)
        joined = ','.join(parts)

        out = f'[{joined}]'
        return out

    # .. plain Python values end the recursion with their repr ..
    if not isinstance(expression, ExpressionBase):
        out = repr(expression)
        return out

    # .. and expression nodes serialize their type and every child attribute,
    # .. gathered from both the instance dict and the slots the AST classes declare.
    names = set(vars(expression))
    for klass in type(expression).__mro__:
        names.update(getattr(klass, '__slots__', ()))

    parts = [type(expression).__name__]
    for name in sorted(names):

        # The evaluation context and the operator implementation describe the engine, not the condition.
        if name in ('context', '_evaluator'):
            continue

        value = getattr(expression, name)
        child_key = build_expression_key(value)
        parts.append(f'{name}={child_key}')

    joined = ' '.join(parts)
    out = f'({joined})'
    return out

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

    def _has_matched(self, match_data:'anydict', condition_cache:'dict_[str, any_]') -> 'bool':
        """ Evaluates the rule's when expression through the cache the whole cycle shares.
        """
        # The counters describe this one evaluation, so they start it at zero.
        self.cache_hits = 0
        self.cache_misses = 0

        out = self._evaluate_with_cache(self.rule.when_impl.statement.expression, match_data, condition_cache)
        return out

    def match(self, data:'anydict', condition_cache:'dict_[str, any_]') -> 'MatchResult':
        """ Match data against the rule using condition caching.
        """
        match_data = self.rule.apply_defaults(data)
        has_matched = self._has_matched(match_data, condition_cache)

        # Build a match result object
        match_result = MatchResult(has_matched)
        match_result.full_name = self.name

        # A match applies the then actions and a non-match still applies the else actions,
        # with an unresolvable reference turned into a loud readable error either way.
        try:
            if has_matched:
                match_result.then = resolve_actions(self.rule.then, match_data)
            else:
                match_result.else_ = resolve_actions(self.rule.else_, match_data)
        except Exception as e:
            raise build_evaluation_error(self.name, e) from e

        return match_result

    def match_then(self, data:'anydict', condition_cache:'dict_[str, any_]') -> 'MatchResult':
        """ Match data against the rule, resolving its then actions and nothing else.

        This is what the merged ruleset answer runs, and it reads only `then` - resolving the
        else actions of every rule that did not fire would resolve actions no caller looks at.
        """
        match_data = self.rule.apply_defaults(data)
        has_matched = self._has_matched(match_data, condition_cache)

        match_result = MatchResult(has_matched)
        match_result.full_name = self.name

        # Only a rule that fired has anything to resolve, with an unresolvable reference
        # turned into a loud readable error.
        if has_matched:
            try:
                match_result.then = resolve_actions(self.rule.then, match_data)
            except Exception as e:
                raise build_evaluation_error(self.name, e) from e

        return match_result

    def _get_cache_key(self, expression:'any_') -> 'str':
        """ Returns the content-based cache key for an expression, computing it at most once per node.
        """
        key = self._expression_keys.get(id(expression))
        if key is None:
            key = build_expression_key(expression)
            self._expression_keys[id(expression)] = key

        return key

    def _evaluate_with_cache(self, expression:'any_', data:'anydict', cache:'dict_[str, any_]') -> 'bool':
        """ Evaluate an expression with caching.
        """
        # Generate a cache key based on the expression
        cache_key = self._get_cache_key(expression)

        # Check if result is already in cache
        if cache_key in cache:
            self.cache_hits += 1
            return cache[cache_key]

        self.cache_misses += 1

        # Fast path for common expression types
        if hasattr(expression, 'type'):
            # Fast path for equality checks
            if expression.type == 'eq':
                try:
                    left_value = expression.left.evaluate(data)
                    right_value = expression.right.evaluate(data)
                    result = left_value == right_value
                    cache[cache_key] = result
                    return result
                except Exception as e:
                    # A value that cannot be evaluated is a loud readable error, never a silent non-match.
                    raise build_evaluation_error(self.name, e) from e

            # Fast path for inequality checks
            elif expression.type == 'ne':
                try:
                    left_value = expression.left.evaluate(data)
                    right_value = expression.right.evaluate(data)
                    result = left_value != right_value
                    cache[cache_key] = result
                    return result
                except Exception as e:
                    # A value that cannot be evaluated is a loud readable error, never a silent non-match.
                    raise build_evaluation_error(self.name, e) from e

        # Fast path for non-logical expressions
        if not isinstance(expression, LogicExpression):
            try:
                result = expression.evaluate(data)
                cache[cache_key] = result
                return bool(result)
            except Exception as e:
                # A value that cannot be evaluated is a loud readable error, never a silent non-match.
                raise build_evaluation_error(self.name, e) from e

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
            # A value that cannot be evaluated is a loud readable error, never a silent non-match.
            raise build_evaluation_error(self.name, e) from e

# ################################################################################################################################
# ################################################################################################################################
