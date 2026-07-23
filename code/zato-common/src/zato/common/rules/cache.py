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
from zato.common.rules.document import resolve_actions
from zato.common.rules.errors import build_evaluation_error
from zato.common.rules.models import MatchResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, dict_
    from zato.common.rules.models import Rule

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

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
    def get_count(item:'any_') -> 'int':
        """ Get the count from an item tuple.
        """
        return item[1]

    sorted_expressions = sorted(expression_count.items(), key=get_count, reverse=True)

    # Add expressions that appear in multiple rules to the result
    for expr, count in sorted_expressions:
        if count > 1:
            result.append(expr)

    return result

def _extract_expressions(expression:'any_') -> 'anylist':
    """ Extract all subexpressions from an expression tree.
    """
    result = [expression]

    # If this is a compound expression, also extract its components
    if hasattr(expression, 'left') and hasattr(expression, 'right'):
        result.extend(_extract_expressions(expression.left))
        result.extend(_extract_expressions(expression.right))

    return result

def precompute_common_expressions(common_expressions:'list[str]', data:'anydict', cache:'dict_[str, any_]') -> 'None':
    """ Precompute results for common expressions.
    """
    # This is a placeholder implementation
    # In a real implementation, we would need to convert the expression strings
    # back to expression objects and evaluate them

    # For now, we'll just log that this function was called
    from logging import getLogger
    logger = getLogger(__name__)
    logger.info(f'Precomputing {len(common_expressions)} common expressions')

def _extract_field_names(expression:'any_') -> 'set[str]':
    """ Extract all field names accessed by an expression.
    """
    field_names = set()

    # If this is a field reference, add it
    if hasattr(expression, 'attribute') and hasattr(expression, 'thing'):
        if expression.thing == 'self' and isinstance(expression.attribute, str):
            field_names.add(expression.attribute)

    # If this has left and right components, process them recursively
    if hasattr(expression, 'left'):
        field_names.update(_extract_field_names(expression.left))

    if hasattr(expression, 'right'):
        field_names.update(_extract_field_names(expression.right))

    return field_names

def build_field_index(rules:'dict_[str, Rule]') -> 'dict_[str, set[str]]':
    """ Build an index of rules by the fields they access.
    """
    field_to_rules = {}

    for rule_name, rule in rules.items():
        # Extract all fields accessed by this rule
        fields = _extract_field_names(rule.when_impl.statement.expression)

        # Add this rule to the index for each field it accesses
        for field in fields:
            if field not in field_to_rules:
                field_to_rules[field] = set()
            field_to_rules[field].add(rule_name)

    return field_to_rules

# ################################################################################################################################
# ################################################################################################################################
