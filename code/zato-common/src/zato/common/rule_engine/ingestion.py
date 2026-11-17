# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# Zato
from zato.common.rule_engine.evaluation import evaluate_input

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.loading import LoadedRules
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class Outcome:
    """ How the evaluation of one input ended.
    """
    Matched  = 'matched'
    No_Match = 'no-match'
    Error    = 'error'

# ################################################################################################################################

Milliseconds_Per_Second = 1000

# ################################################################################################################################
# ################################################################################################################################

def evaluate_decision(loaded:'LoadedRules', data:'anydict') -> 'anydict':
    """ Evaluates one input against the loaded rules and returns the outcome, the outputs,
    the fired statements, the error and the duration.
    """
    # Time the complete evaluation, which never raises - an input a rule
    # cannot evaluate comes back with a readable error instead ..
    started = monotonic()
    evaluated = evaluate_input(loaded, data)
    elapsed = monotonic() - started

    # .. the duration is reported in whole milliseconds ..
    duration_ms = int(elapsed * Milliseconds_Per_Second)

    error = evaluated['error']
    fired = evaluated['fired']
    actual = evaluated['actual']

    # .. the outcome names how the evaluation ended ..
    if error:
        outcome = Outcome.Error
    elif fired:
        outcome = Outcome.Matched
    else:
        outcome = Outcome.No_Match

    # .. and the result is returned to the caller.
    out = {
        'outcome':     outcome,
        'actual':      actual,
        'fired':       fired,
        'error':       error,
        'duration_ms': duration_ms,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################
