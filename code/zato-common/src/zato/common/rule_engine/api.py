# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.models import Ruleset, MatchResult, Rule, rule_from_document
from zato.common.rule_engine.cache import CachedRule
from zato.common.rule_engine.evaluation import first_matching_rule

# ################################################################################################################################
# ################################################################################################################################

# stdlib
from logging import getLogger
from pathlib import Path
from threading import RLock

# Zato
from zato.common.rule_engine.parser import parse_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dict_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RulesManager:
    """ Rules manager with condition caching.
    """

    def __init__(self) -> 'None':
        self._all_rules = {}
        self._rulesets = {}
        self._lock = RLock()
        self.cached_rules:'dict_[str, CachedRule]' = {}

    def get_rule(self, full_name:'str') -> 'Rule':
        """ Returns one loaded rule by its full name.
        """
        out = self._all_rules[full_name]
        return out

    def __getitem__(self, name:'str') -> 'Rule | Ruleset':
        return getattr(self, name)

    def __getattr__(self, name:'str') -> 'Rule | Ruleset':

        # Check if we have a matching ruleset
        if name in self._rulesets:

            # .. if yes, return it to the caller ..
            return self._rulesets[name]

        # .. try to see if we have a rule of that name ..
        elif name in self._all_rules:

            # .. if yes, return that rule ..
            return self._all_rules[name]

        # .. otherwise, give up
        else:
            raise AttributeError(f'No such rule, ruleset or attribute -> {name}')

    def match_first(self, data:'strdict', rules:'any_') -> 'MatchResult | None':
        """ Returns the first of the named rules that matches, with condition caching.

        This is the explicit-list question, not the ruleset answer - a caller who wants what a
        whole ruleset decides asks `Ruleset.match`, which merges every rule that fires instead.
        """
        # Determine which rules to check
        rule_names = [rules] if isinstance(rules, str) else rules

        cached_rules = []
        for rule_name in rule_names:
            cached_rule = self.cached_rules.get(rule_name)

            # Every loaded rule has its cached form, so a name without one is the name of no rule,
            # and saying so is more useful than quietly checking one rule fewer.
            if cached_rule is None:
                raise AttributeError(f'No such rule -> {rule_name}')

            cached_rules.append(cached_rule)

        out = first_matching_rule(cached_rules, data)
        return out

# ################################################################################################################################
# ################################################################################################################################

    def load_parsed_rules(self, parsed:'strdict', ruleset_name:'str') -> 'strlist':

        # Our response to produce
        out = []

        # First, delete that ruleset completely ..
        previous = self._rulesets.pop(ruleset_name, None)

        # .. including every rule it used to hold, so a reload never keeps firing rules
        # .. that the new version of the ruleset no longer has ..
        if previous is not None:
            for full_name in previous._rules:
                _ = self._all_rules.pop(full_name, None)
                _ = self.cached_rules.pop(full_name, None)

        # .. recreate it ..
        ruleset = Ruleset(ruleset_name)
        self._rulesets[ruleset.name] = ruleset

        # .. go through each rule found ..
        # .. and note that we're iterating the full names alpabetically (because parsed is a SortedDict) ..
        # .. so the ruleset's own dict will also always iterate over them alphabetically ..
        for document in parsed.values():

            # .. build a new rule out of its document ..
            rule = rule_from_document(document)
            if rule is None:
                continue

            # .. make sure to delete it first from the global dict ..
            _ = self._all_rules.pop(rule.full_name, None)

            # .. we can now add it to the global dict ..
            self._all_rules[rule.full_name] = rule

            # Create a cached version of the rule
            cached_rule = CachedRule(rule)
            self.cached_rules[rule.full_name] = cached_rule

            # .. add both forms to the ruleset as well ..
            ruleset.add_rule(rule, cached_rule)

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
            logger.info(f'Loaded rules (api.py): {result}')

            # .. and tell the caller what we loaded.
            return result

# ################################################################################################################################
# ################################################################################################################################
