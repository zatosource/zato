# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from pathlib import Path
from threading import RLock

# Zato
from zato.common.rules.cache import CachedRule
from zato.common.rules.models import Ruleset, Rule, rule_from_document
from zato.common.rules.parser import parse_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dict_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RuleLoader:
    """ Handles loading rules from files and directories.
    """

    def __init__(self):
        self._lock = RLock()

    def load_parsed_rules(self, parsed:'strdict', ruleset_name:'str',
                          all_rules:'dict_[str, Rule]', rulesets:'dict_[str, Ruleset]',
                          cached_rules:'dict_[str, any_]') -> 'strlist':
        """ Load rules from parsed data.
        """
        # Our response to produce
        out = []

        # First, delete that ruleset completely ..
        _ = rulesets.pop(ruleset_name, None)

        # .. recreate it ..
        ruleset = Ruleset(ruleset_name)
        rulesets[ruleset.name] = ruleset

        # .. go through each rule found ..
        # .. and note that we're iterating the full names alpabetically (because parsed is a SortedDict) ..
        # .. so the ruleset's own dict will also always iterate over them alphabetically ..
        for document in parsed.values():

            # .. build a new rule out of its document ..
            rule = rule_from_document(document)
            if rule is None:
                continue

            # .. make sure to delete it first from the global dict ..
            _ = all_rules.pop(rule.full_name, None)

            # .. we can now add it to the global dict ..
            all_rules[rule.full_name] = rule

            # .. add it to the ruleset as well ..
            ruleset.add_rule(rule)

            # Create a cached version of the rule
            cached_rules[rule.full_name] = CachedRule(rule)

            # .. append it for later use ..
            out.append(rule.full_name)

        # .. finally, we can return a list of what we loaded.
        return out

    def load_rules_from_file(self, file_path:'str | Path',
                            all_rules:'dict_[str, Rule]', rulesets:'dict_[str, Ruleset]',
                            cached_rules:'dict_[str, any_]') -> 'strlist':
        """ Load rules from a file.
        """
        file_name = Path(file_path).name
        file_name = file_name.replace('.zrules', '')

        with self._lock:
            # Parse the contents of the file ..
            parsed = parse_file(file_path, file_name)

            # .. load it all ..
            result = self.load_parsed_rules(parsed, file_name, all_rules, rulesets, cached_rules)

            # .. log what was loaded ...
            logger.info(f'Loaded rules (loader.py): {result}')

            # .. and tell the caller what we loaded.
            return result

    def load_rules_from_directory(self, root_dir:'str | Path',
                                 all_rules:'dict_[str, Rule]', rulesets:'dict_[str, Ruleset]',
                                 cached_rules:'dict_[str, any_]') -> 'strlist':
        """ Load rules from a directory.
        """
        # Our response to produce
        out = []

        # Go through all the matching files ..
        for elem in Path(root_dir).glob('*.zrules'):

            # .. read them all in.
            result = self.load_rules_from_file(elem, all_rules, rulesets, cached_rules)

            # .. append it for later use ..
            out.extend(result)

        # .. and return the list of what was loaded to our caller.
        return out

# ################################################################################################################################
# ################################################################################################################################
