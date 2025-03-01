# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from pathlib import Path
from threading import RLock

# rule-engine
from rule_engine import Rule as RuleImpl

# Zato
from zato.common.marshal_.api import Model
from zato.common.rules.parser import parse_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dict_, strdict

# ################################################################################################################################
# ################################################################################################################################

def handle(self): # type: ignore

    input = 'abc = 123'
    rules = ['hr_ABC_BANK_001', 'hr_TELCO_002', 'hr_Payments_003']

    # Match a rule by its full name
    result = self.rules.default_ABC_BANK_001.match(input)

    # Match all rules from a specific container
    result = self.rules.hr.match(input)
    result = self.rules['hr'].match(input)

    # Match named rules, no matter which container they're from
    result = self.rules.match(input, rules=rules)

    # Match a named rule from the demo container
    result = self.rules.demo.Payments_003.match(input)
    result = self.rules.demo['Payments_003'].match(input)

    # Match a specific rule from a specific container
    result = self.rules.hr.rule_4.match(input)
    result = self.rules.hr['rule_4'].match(input)
    result = self.rules['hr']['rule_4'].match(input)

    print(111, result)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Rule(Model):
    full_name: 'str'
    name: 'str'
    container_name: 'str'
    docs: 'str'
    invoke: 'strdict'
    when: 'str'
    when_impl: 'RuleImpl'
    then: 'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Container(Model):
    name: 'str'
    _rules: 'dict_[str, Rule]'

    def __init__(self, name:'str') -> 'None':
        self.name = name
        self._rules = {}

    def add_rule(self, rule:'Rule') -> 'None':
        self._rules[rule.full_name] = rule

    def delete_rule(self, full_name:'str') -> 'None':
        _ = self._rules.pop(full_name, None)

# ################################################################################################################################
# ################################################################################################################################

class RulesManager:

    _all_rules: 'dict_[str, Rule]'
    _containers: 'dict_[str, Container]'

    def __init__(self) -> 'None':
        self._all_rules = {}
        self._containers = {}
        self._lock = RLock()

# ################################################################################################################################
# ################################################################################################################################

    def load_parsed_rules(self, parsed:'strdict') -> 'None':

        # .. go through each rule found ..
        for full_name, rule_data in parsed.items():

            # .. build a new rule ..
            rule = Rule()
            rule.full_name = full_name
            rule.name = rule_data['name']
            rule.container_name = rule_data['container_name']
            rule.when = rule_data['when']
            rule.when_impl = RuleImpl(rule.when)
            rule.then = rule_data['then']
            rule.docs = rule_data.get('docs', '')
            rule.invoke = rule_data.get('invoke', '')

            # .. make sure to delete it first from the global dict ..
            _ = self._all_rules.pop(rule.full_name, None)

            # .. now, get the container to delete it from ..
            if container := self._containers.get(rule.container_name):

                # .. delete that rule from the container as well ..
                container.delete_rule(rule.full_name)

            # .. or create a container if we didn't have one ..
            else:
                container = Container(rule.container_name)
                self._containers[container.name] = container

            # .. we can now add it to the global dict ..
            self._all_rules[rule.full_name] = rule

            # .. and add our rule to it.
            container.add_rule(rule)

# ################################################################################################################################
# ################################################################################################################################

    def load_rules_from_file(self, file_path:'str | Path', file_name:'str') -> 'None':

        with self._lock:

            # Parse the contents of the file ..
            parsed = parse_file(file_path, file_name)

            # .. and load it all.
            self.load_parsed_rules(parsed)

# ################################################################################################################################
# ################################################################################################################################

    def load_rules_from_directory(self, root_dir:'str') -> 'None':

        # Go through all the matching files ..
        for elem in Path(root_dir).glob('*.zrules'):

            # .. and read them all in.
            self.load_rules_from_file(elem, elem.stem)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == "__main__":

    # stdlib
    import sys

    root_dir = sys.argv[1]

    manager = RulesManager()
    _ = manager.load_rules_from_directory(root_dir)

# ################################################################################################################################
# ################################################################################################################################
