# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from typing import Iterable

# Zato
from zato.common.rule_engine.errors import RuleEvaluationError
from zato.common.rule_engine.table import StatementSeverity

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.cache import CachedRule
    from zato.common.rule_engine.loading import LoadedRules
    from zato.common.rule_engine.models import MatchResult
    from zato.common.typing_ import anydict, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

cached_rule_iterable = Iterable['CachedRule']

# ################################################################################################################################

# What a fired rule's trace line says when its document carries no statement.
Default_Statement_Severity = StatementSeverity.Info

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RulesetOutcome:
    """ What a whole ruleset decided for one input.

    This is the one ruleset answer, given by every door into the engine - the in-process
    `Ruleset.match` and the REST invocation alike. It is a plain dataclass rather than a
    marshalled model because it never crosses a serialization boundary itself, the REST
    side builds its own payload out of it.
    """

    has_matched: 'bool'
    then:        'strdict'
    fired:       'dictlist'

    def __init__(self) -> 'None':
        self.has_matched = False
        self.then = {}
        self.fired = []

    def __bool__(self) -> 'bool':
        return self.has_matched

# ################################################################################################################################
# ################################################################################################################################

def _statement_of(document:'anydict') -> 'anydict':
    """ The plain-language statement a fired rule reports - its own, or its docs as the default.
    """
    statement = document.get('statement')

    if statement is None:
        statement = {'text': document['docs'], 'severity': Default_Statement_Severity}

    return statement

# ################################################################################################################################

def _trace_entry(cached_rule:'CachedRule') -> 'anydict':
    """ The trace line one fired rule contributes - which rule fired and what it says it did.
    """
    statement = _statement_of(cached_rule.rule.document)

    out = {'rule': cached_rule.name, 'statement': statement['text'], 'severity': statement['severity']}
    return out

# ################################################################################################################################
# ################################################################################################################################

def evaluate_ruleset(cached_rules:'cached_rule_iterable', data:'anydict') -> 'RulesetOutcome':
    """ Evaluates one input against every rule of a ruleset and merges what fired.

    Every rule is visited and every rule that fires contributes its assignments, in rule order,
    so a later rule assigning a target another one already assigned has the final say. A rule
    that did not fire contributes nothing at all - else actions belong to the single-rule
    contract of `Rule.match`, not to the answer of a whole ruleset.

    A rule that cannot evaluate the input raises, so a half-evaluated ruleset never comes back
    looking like an answer.
    """

    # Our response to produce
    out = RulesetOutcome()

    # One cache for the whole call, so a condition several rules share is evaluated
    # once per input rather than once per rule.
    condition_cache = {}

    for cached_rule in cached_rules:
        result = cached_rule.match_then(data, condition_cache)

        # A rule that did not fire has nothing to contribute ..
        if not result:
            continue

        # .. and one that did contributes its trace line and its assignments.
        out.has_matched = True
        out.fired.append(_trace_entry(cached_rule))
        out.then.update(result.then)

    return out

# ################################################################################################################################

def first_matching_rule(cached_rules:'cached_rule_iterable', data:'anydict') -> 'MatchResult | None':
    """ Returns the result of the first rule of an explicit list that matches, None if none does.

    This answers a different question from `evaluate_ruleset` - which of these named rules applies
    first - so it stops at the first match and it does return that rule's else actions on the way,
    because a caller asking about one rule at a time is asking the single-rule question.
    """

    # The rules of one question share one cache, exactly as they do on the merged path.
    condition_cache = {}

    for cached_rule in cached_rules:
        if result := cached_rule.match(data, condition_cache):
            return result

# ################################################################################################################################
# ################################################################################################################################

def evaluate_input(loaded:'LoadedRules', data:'anydict') -> 'anydict':
    """ The ruleset answer for one input, in the shape the screens and the decision log read.

    The outcome itself comes from `evaluate_ruleset`, so what a test screen shows and what a
    service gets in process are the same answer. The difference is here at the boundary - a rule
    that cannot evaluate the input comes back as a readable message rather than as an exception,
    because every caller of this function shows it to a person.
    """
    fired = []
    actual = {}
    error = ''

    cached_rules = []
    for full_name in loaded.rule_names:
        cached_rules.append(loaded.manager.cached_rules[full_name])

    try:
        outcome = evaluate_ruleset(cached_rules, data)
    except RuleEvaluationError as e:
        error = str(e)
    else:
        actual = outcome.then
        fired = outcome.fired

    out = {'actual': actual, 'fired': fired, 'error': error}
    return out

# ################################################################################################################################
# ################################################################################################################################
