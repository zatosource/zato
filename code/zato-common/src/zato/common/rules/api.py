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
    from zato.common.typing_ import any_, anydict, dict_, strdict

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
    invoke: 'strdict'
    when: 'str'
    when_impl: 'RuleImpl'
    then: 'str'

    def __getattr__(self, name:'str') -> 'any_':
        pass

    def match(self, data:'anydict') -> 'MatchResult':

        # Evaluate our rule ..
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

class RulesManager:

    _all_rules: 'dict_[str, Rule]'
    _containers: 'dict_[str, Container]'

    def __init__(self) -> 'None':
        self._all_rules = {}
        self._containers = {}
        self._lock = RLock()

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

        # Go through our input ..
        for _rule_name in rules:

            # .. get the actual rule ..
            rule = self[_rule_name]

            # .. if we have a match ..
            if result := rule.match(data):

                # .. return it to our caller.
                return result

# ################################################################################################################################
# ################################################################################################################################

    def load_parsed_rules(self, parsed:'strdict', container_name:'str') -> 'None':

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
            rule.when_impl = RuleImpl(rule.when)
            rule.then = rule_data['then']
            rule.docs = rule_data.get('docs', '')
            rule.invoke = rule_data.get('invoke', '')

            # .. make sure to delete it first from the global dict ..
            _ = self._all_rules.pop(rule.full_name, None)

            # .. we can now add it to the global dict ..
            self._all_rules[rule.full_name] = rule

            # .. and to the container as well.
            container.add_rule(rule)

# ################################################################################################################################
# ################################################################################################################################

    def load_rules_from_file(self, file_path:'str | Path', file_name:'str') -> 'None':

        with self._lock:

            # Parse the contents of the file ..
            parsed = parse_file(file_path, file_name)

            # .. and load it all.
            self.load_parsed_rules(parsed, file_name)

# ################################################################################################################################
# ################################################################################################################################

    def load_rules_from_directory(self, root_dir:'str') -> 'None':

        # Go through all the matching files ..
        for elem in Path(root_dir).glob('*.zrules'):

            # .. and read them all in.
            self.load_rules_from_file(elem, elem.stem)

# ################################################################################################################################
# ################################################################################################################################

def handle(self): # type: ignore

    input = 'abc = 123'
    rules = ['hr_ABC_BANK_001', 'hr_TELCO_002', 'hr_Payments_003']

    # 1) Accept the first matching rule from a specific container (by attr)
    result = self.rules.hr.match(input)

    # 2) Accept the first matching rule from a specific container (by dict)
    result = self.rules['hr'].match(input)

    # 3) Accept the first matching rule, no matter which container they're from
    result = self.rules.match(input, rules=rules)

    # 4) Match a named rule from the demo container (by attr)
    result = self.rules.demo.Payments_003.match(input)

    # 5) Match a named rule from the demo container (by dict)
    result = self.rules.demo['Payments_003'].match(input)

    # 6) Accept a named rule by its name (by attr)
    result = self.rules.demo_4.match(input)

    # 7) Accept a named rule by its name (by dict)
    result = self.rules['demo_4'].match(input)

    print(111, result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == "__main__":

    # stdlib
    import sys

    root_dir = sys.argv[1]

    rules = RulesManager()
    _ = rules.load_rules_from_directory(root_dir)

    # print(111, rules._all_rules)

    data = {'abc': 123}

    # 1) Accept the first matching rule from a specific container (by attr)
    # result2 = rules.demo.match(data)
    # print(222, result2)

    # 2) Accept the first matching rule from a specific container (by dict)
    # result = rules['demo'].match(data)
    # print(222, result2)

    # 3) Accept the first matching rule, no matter which container they're from
    _rules = ['demo_rule_4b', 'demo_rule_4']
    result3 = rules.match(data, rules=_rules)
    print(333, result3)

    # 4) Match a named rule from the demo container (by attr)
    result4 = rules.demo.rule_4.match(data)
    print(444, result4)

    # 5) Match a named rule from the demo container (by dict)
    result5 = rules.demo['rule_4'].match(data) # type: ignore
    print(555, result5)

    # 6) Accept a named rule by its name (by attr)
    result6 = rules.demo_rule_4.match(data)
    print(666, result6)

    # 7) Accept a named rule by its name (by attr)
    result7 = rules['demo_rule_4'].match(data)
    print(777, result7)

# ################################################################################################################################
# ################################################################################################################################
