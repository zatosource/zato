from typing import Any

from copy import deepcopy
from dataclasses import dataclass
from logging import getLogger
from rule_engine import Rule as RuleImpl
from zato.common.marshal_.api import Model
from zato.common.typing_ import any_, anydict, dict_, strdict

def resolve_then_values(then_dict: Any, data: Any) -> None: ...

class MatchResult(Model):
    _has_matched: bool
    then: any_
    full_name: str
    def __init__(self: Any, has_matched: bool) -> None: ...
    def __bool__(self: Any) -> bool: ...

class Rule(Model):
    full_name: str
    name: str
    container_name: str
    docs: str
    defaults: strdict
    invoke: strdict
    when: str
    when_impl: RuleImpl
    then: str
    def __getattr__(self: Any, name: str) -> any_: ...
    def match(self: Any, data: anydict) -> MatchResult: ...

class Container(Model):
    name: str
    _rules: dict_[str, Rule]
    def __init__(self: Any, name: str) -> None: ...
    def __getitem__(self: Any, name: str) -> Rule: ...
    def __getattr__(self: Any, name: str) -> Rule: ...
    def add_rule(self: Any, rule: Rule) -> None: ...
    def delete_rule(self: Any, full_name: str) -> None: ...
    def match(self: Any, data: anydict) -> MatchResult | None: ...
