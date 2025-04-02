# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato - import all components and re-export them
from zato.common.rules.models import Container, MatchResult, Rule
from zato.common.rules.cache import CachedRule

# ################################################################################################################################
# ################################################################################################################################

# stdlib
from copy import deepcopy
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from threading import RLock
from time import time

# rule-engine
from rule_engine import Rule as RuleImpl
from rule_engine.ast import ExpressionBase, LogicExpression

# Zato
from zato.common.marshal_.api import Model
from zato.common.rules.parser import parse_file

# ################################################################################################################################
# ################################################################################################################################

# For flake8
Container = Container
MatchResult = MatchResult
Rule = Rule

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, bool_, dict_, float_, int_, strdict, strlist

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

class RulesManager:
    """ Rules manager with condition caching.
    """

    def __init__(self) -> 'None':
        self._all_rules = {}
        self._containers = {}
        self._lock = RLock()
        self.cached_rules = {}  # type: dict_[str, CachedRule]
        self.performance_stats = {
            'total_evaluations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0.0
        }  # type: dict_[str, int_ | float_]

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

    def _update_stats(self, condition_cache:'dict_[str, any_]', cached_rule:'CachedRule | None'=None, start_time:'float_'=0) -> 'None':
        """ Update performance statistics.
        """
        self.performance_stats['total_evaluations'] += 1

        if cached_rule:
            self.performance_stats['cache_hits'] += cached_rule.cache_hits
            self.performance_stats['cache_misses'] += cached_rule.cache_misses

        self.performance_stats['total_time'] += time() - start_time

    def get_performance_stats(self) -> 'dict_[str, int_ | float_]':
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

    def load_parsed_rules(self, parsed:'strdict', container_name:'str') -> 'strlist':

        # Our response to produce
        out = []

        # First, delete that container completely ..
        _ = self._containers.pop(container_name, None)

        # .. recreate it ..
        container = Container(container_name)
        self._containers[container.name] = container

        # .. go through each rule found ..
        # .. and note that we're iterating the full names alpabetically (because parsed is a SortedDict) ..
        # .. so the container's own dict will also always iterate over them alphabetically ..
        for full_name, rule_data in parsed.items():

            # .. build a new rule ..
            rule = Rule()
            rule.full_name = full_name
            rule.name = rule_data['name']
            rule.container_name = rule_data['container_name']
            rule.when = rule_data['when']

            try:
                rule.when_impl = RuleImpl(rule.when)
            except Exception as e:
                logger.warning(f'Rule loading error -> {full_name} -> {rule.when} -> {e}')
                continue

            rule.then = rule_data['then']
            rule.defaults = rule_data.get('defaults', {})
            rule.docs = rule_data.get('docs', '')
            rule.invoke = rule_data.get('invoke', '')

            # .. make sure to delete it first from the global dict ..
            _ = self._all_rules.pop(rule.full_name, None)

            # .. we can now add it to the global dict ..
            self._all_rules[rule.full_name] = rule

            # .. add it to the container as well ..
            container.add_rule(rule)

            # Create a cached version of the rule
            self.cached_rules[rule.full_name] = CachedRule(rule)

            # .. append it for later use ..
            out.append(rule.full_name)

        # .. finally, we can return a list of what we loaded.
        return out

# ################################################################################################################################
# ################################################################################################################################

    def load_rules_from_file(self, file_path:'str | Path') -> 'strlist':

        file_name = Path(file_path).name
        file_name = file_name.replace('.zrules', '')

        with self._lock:

            # Parse the contents of the file ..
            parsed = parse_file(file_path, file_name)

            # .. load it all ..
            result = self.load_parsed_rules(parsed, file_name)

            # .. log what was loaded ...
            logger.info(f'Loaded rules: {result}')

            # .. and tell the caller what we loaded.
            return result

# ################################################################################################################################
# ################################################################################################################################

    def load_rules_from_directory(self, root_dir:'str | Path') -> 'strlist':

        # Our response to produce
        out = []

        # Go through all the matching files ..
        for elem in Path(root_dir).glob('*.zrules'):

            # .. read them all in.
            result = self.load_rules_from_file(elem)

            # .. append it for later use ..
            out.extend(result)

        # .. and return the list of what was loaded to our caller.
        return out

# ################################################################################################################################
# ################################################################################################################################
