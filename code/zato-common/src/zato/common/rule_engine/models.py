# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections.abc import Mapping
from dataclasses import dataclass
from logging import getLogger

# rule-engine
from rule_engine import Context as ContextImpl, Rule as RuleImpl

# Zato
from zato.common.marshal_.api import Model
from zato.common.rule_engine.document import compile_when, resolve_actions, resolve_defaults
from zato.common.rule_engine.errors import build_evaluation_error
from zato.common.rule_engine.evaluation import evaluate_ruleset, RulesetOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.cache import CachedRule
    from zato.common.typing_ import any_, anydict, dict_, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class DataView(Mapping):
    """ A read-only view of a dict that is not a dict itself - the library copies and converts
    every dict it resolves, key by key and value by value, whereas a plain mapping passes through as is.
    """
    __slots__ = ('_data',)

    def __init__(self, data:'anydict') -> 'None':
        self._data = data

    def __getitem__(self, key:'str') -> 'any_':
        return self._data[key]

    def __iter__(self) -> 'any_':
        return iter(self._data)

    def __len__(self) -> 'int':
        return len(self._data)

# ################################################################################################################################

class Context(ContextImpl):
    """ The evaluation context of every rule.
    """

    def resolve(self, thing:'any_', name:'str', scope:'any_'=None) -> 'any_':

        # A top-level symbol that is a dict, e.g. the whole fact a rule looks at, is handed out as a view,
        # otherwise the library would convert all of it on every single evaluation
        out = super().resolve(thing, name, scope)

        if isinstance(out, dict):
            out = DataView(out)

        return out

    def resolve_attribute(self, thing:'any_', object_:'anydict', name:'str') -> 'any_':

        # The library types the whole mapping on each access before it looks the name up
        # among the built-in attributes and falls back to the key - so the key comes first here
        if isinstance(object_, Mapping) and name in object_:
            out = object_[name]
            return out

        out = super().resolve_attribute(thing, object_, name)
        return out

# The one context every rule is compiled with
_context = Context()

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MatchResult(Model):
    _has_matched: 'bool'
    then:'strdict'
    else_:'strdict'
    full_name:'str'

    def __init__(self, has_matched:'bool') -> 'None':
        self._has_matched = has_matched

        # A match fills in the then actions and a non-match the else ones, so one of the two
        # always stays empty. Both start out empty rather than absent, because reading the
        # side that did not apply is normal and must answer with nothing, not raise.
        self.then = {}
        self.else_ = {}

    def __bool__(self) -> 'bool':
        return self._has_matched

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Rule(Model):
    full_name: 'str'
    name: 'str'
    ruleset_name: 'str'
    docs: 'str'
    defaults: 'strdict'
    document: 'anydict'
    when: 'str'
    when_impl: 'RuleImpl'
    then: 'dictlist'
    else_: 'dictlist'

# ################################################################################################################################

    def apply_defaults(self, data:'anydict') -> 'anydict':
        """ Returns data with any missing default values filled in, copying only when needed.
        """

        # Without defaults there is nothing to fill in ..
        if not self.defaults:
            return data

        # .. otherwise, copy the input lazily, only if a default is actually missing ..
        modified_data = None

        for key, value in self.defaults.items():
            if key not in data:

                # .. the first missing default triggers the copy - a shallow one, only top-level keys are added ..
                if modified_data is None:
                    modified_data = dict(data)

                # .. and each missing default lands in the copy.
                modified_data[key] = value

        out = modified_data if modified_data is not None else data
        return out

# ################################################################################################################################

    def match(self, data:'anydict') -> 'MatchResult':

        # Fill in defaults for any keys the input does not provide ..
        match_data = self.apply_defaults(data)

        # .. evaluate our rule with the appropriate data, turning a missing value or
        # .. a type mismatch into a loud readable error instead of a silent non-match ..
        try:
            has_matched = self.when_impl.matches(match_data)
        except Exception as e:
            raise build_evaluation_error(self.full_name, e) from e

        # .. and build a result object ..
        match_result = MatchResult(has_matched)
        match_result.full_name = self.full_name

        # .. a match applies the then actions and a non-match still applies the else actions,
        # .. with an unresolvable reference turned into a loud readable error either way.
        try:
            if has_matched:
                match_result.then = resolve_actions(self.then, match_data)
            else:
                match_result.else_ = resolve_actions(self.else_, match_data)
        except Exception as e:
            raise build_evaluation_error(self.full_name, e) from e

        return match_result

# ################################################################################################################################
# ################################################################################################################################

def rule_from_document(document:'anydict') -> 'Rule | None':
    """ Builds a runtime Rule out of a parsed rule document, returning None if its when expression will not compile.
    """

    # Carry over the document and its identity ..
    rule = Rule()
    rule.full_name = document['full_name']
    rule.name = document['name']
    rule.ruleset_name = document['ruleset_name']
    rule.document = document
    rule.docs = document['docs']

    # .. defaults resolve into plain values used at match time ..
    rule.defaults = resolve_defaults(document['defaults'])

    # .. the when expression is compiled from the conditions and joiners ..
    rule.when = compile_when(document)

    try:
        rule.when_impl = RuleImpl(rule.when, context=_context)
    except Exception as e:
        logger.warning(f'Rule loading error -> {rule.full_name} -> {rule.when} -> {e}')
        return None

    # .. and both action lists stay as tagged nodes, resolved per match.
    rule.then = document['then']
    rule.else_ = document['else']

    return rule

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Ruleset(Model):
    name: 'str'
    _rules: 'dict_[str, Rule]'
    _cached_rules: 'dict_[str, CachedRule]'

    def __init__(self, name:'str') -> 'None':
        self.name = name

        # Each rule is held in both forms its two doors need - the plain rule that a caller
        # naming one rule gets back, and the cached one that the ruleset answer evaluates
        # through, because only that form can share a condition cache across rules.
        self._rules = {}
        self._cached_rules = {}

    def __getitem__(self, name:'str') -> 'Rule':
        return getattr(self, name)

    def __getattr__(self, name:'str') -> 'Rule':
        full_name = self.name + '_' + name
        if rule := self._rules.get(full_name):
            return rule
        else:
            raise AttributeError(f'No such rule -> {full_name}')

# ################################################################################################################################

    def add_rule(self, rule:'Rule', cached_rule:'CachedRule') -> 'None':
        self._rules[rule.full_name] = rule
        self._cached_rules[rule.full_name] = cached_rule

# ################################################################################################################################

    def delete_rule(self, full_name:'str') -> 'None':
        _ = self._rules.pop(full_name, None)
        _ = self._cached_rules.pop(full_name, None)

# ################################################################################################################################

    def match(self, data:'anydict') -> 'RulesetOutcome':
        """ Returns what this ruleset decides for one input, merging every rule that fires.

        This is the same answer the REST door gives for the same input, from the same core,
        so a ruleset cannot decide one thing for a service in process and another over HTTP.
        """
        out = evaluate_ruleset(self._cached_rules.values(), data)
        return out

# ################################################################################################################################
# ################################################################################################################################
