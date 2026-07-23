# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# rule-engine
from rule_engine.errors import SymbolResolutionError

# ################################################################################################################################
# ################################################################################################################################

class Severity:
    """ How serious a validation finding is - errors block, warnings inform.
    """
    Error   = 'error'
    Warning = 'warning'

# ################################################################################################################################
# ################################################################################################################################

class RuleEvaluationError(Exception):
    """ Raised when a rule cannot be evaluated against input data.

    The message is always readable in domain terms - a missing value or a type mismatch never
    turns into a silent non-match, which is the engine guarantee behind rule evaluation.
    """

    def __init__(self, rule_name:'str', field:'str', message:'str') -> 'None':
        super().__init__(message)
        self.rule_name = rule_name
        self.field = field

# ################################################################################################################################
# ################################################################################################################################

def build_evaluation_error(rule_name:'str', exception:'Exception') -> 'RuleEvaluationError':
    """ Translates an underlying evaluation exception into a readable RuleEvaluationError.
    """

    # An already readable error passes through unchanged so nested evaluation never double-wraps it ..
    if isinstance(exception, RuleEvaluationError):
        out = exception

    # .. a missing symbol means the input has no value for a term the rule needs ..
    elif isinstance(exception, SymbolResolutionError):
        field = exception.symbol_name
        message = f'Rule {rule_name} cannot run - the input has no value for {field!r}'
        out = RuleEvaluationError(rule_name, field, message)

    # .. and everything else keeps the underlying reason, prefixed with the rule it broke.
    else:
        message = f'Rule {rule_name} cannot run - {exception}'
        out = RuleEvaluationError(rule_name, '', message)

    return out

# ################################################################################################################################
# ################################################################################################################################
