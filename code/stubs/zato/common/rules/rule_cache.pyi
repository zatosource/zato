from typing import Any

from copy import deepcopy
from logging import getLogger
from rule_engine.ast import ExpressionBase, LogicExpression
from zato.common.rules.api import MatchResult, Rule
from zato.common.typing_ import any_, anydict, bool_, dict_

class CachedRule:
    def __init__(self: Any, rule: Rule) -> None: ...
    def match(self: Any, data: anydict, condition_cache: dict_[str, any_] = ...) -> MatchResult: ...
    def _evaluate_with_cache(self: Any, expression: ExpressionBase, data: anydict, cache: dict_[str, any_]) -> bool_: ...
