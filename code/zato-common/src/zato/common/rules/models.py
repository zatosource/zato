# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass
from logging import getLogger

# rule-engine
from rule_engine import Rule as RuleImpl

# Zato
from zato.common.marshal_.api import Model

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dict_, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MatchResult(Model):
    _has_matched: 'bool'
    then:'any_'
    full_name:'str'

    def __init__(self, has_matched:'bool') -> 'None':
        self._has_matched = has_matched

    def __bool__(self) -> 'bool':
        return self._has_matched

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Rule(Model):
    full_name: 'str'
    name: 'str'
    container_name: 'str'
    docs: 'str'
    defaults: 'strdict'
    invoke: 'strdict'
    when: 'str'
    when_impl: 'RuleImpl'
    then: 'str'

    def __getattr__(self, name:'str') -> 'any_':
        pass

    def match(self, data:'anydict') -> 'MatchResult':

        # Local variables
        needs_defaults = False

        # Check if we need to add some of the default values ..
        if self.defaults:
            for key in self.defaults:
                if key not in data:
                    needs_defaults = True
                    break

        # .. populate the data with any missing elements ..
        if needs_defaults:

            # .. make a deep copy so as not to change the input ..
            data = deepcopy(data)

            # .. now, add all the missing keys ..
            for key, value in self.defaults.items():
                if key not in data:
                    data[key] = value

        # .. evaluate our rule ..
        has_matched = self.when_impl.matches(data)

        # .. build a result object ..
        match_result = MatchResult(has_matched)

        # .. populate all the attributes ..
        match_result.then = self.then
        match_result.full_name = self.full_name

        # .. finally, return the result to the caller.
        return match_result

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Container(Model):
    name: 'str'
    _rules: 'dict_[str, Rule]'

    def __init__(self, name:'str') -> 'None':
        self.name = name
        self._rules = {}

    def __getitem__(self, name:'str') -> 'Rule':
        return getattr(self, name)

    def __getattr__(self, name:'str') -> 'Rule':
        full_name = self.name + '_' + name
        if rule := self._rules.get(full_name):
            return rule
        else:
            raise AttributeError(f'No such rule -> {full_name}')

    def add_rule(self, rule:'Rule') -> 'None':
        self._rules[rule.full_name] = rule

    def delete_rule(self, full_name:'str') -> 'None':
        _ = self._rules.pop(full_name, None)

    def match(self, data:'anydict') -> 'MatchResult | None':

        # Go through all the rules we have ..
        for rule in self._rules.values():

            # .. if we have a match ..
            if match_result := rule.match(data):

                # .. return it to our caller.
                return match_result

# ################################################################################################################################
# ################################################################################################################################
