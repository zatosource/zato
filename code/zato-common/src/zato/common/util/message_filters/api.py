# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# jsonata-python
from jsonata import Jsonata

# Zato
from zato.common.typing_ import any_
from zato.common.util.message_filters.cache import get_compiled
from zato.common.util.message_filters.common import FilterResult, Kind_Evaluation_Error, Kind_Syntax_Error, Kind_Too_Long, \
    Max_Expression_Length
from zato.common.util.truncate.measure import get_size

# ################################################################################################################################
# ################################################################################################################################

def validate_expression(expression:'str') -> 'None':
    """ Compiles a JSONata expression, raising an exception if its syntax is invalid.
    This is the admin-time path - configuration screens and imports call it to reject broken expressions early.
    """
    _ = Jsonata(expression)

# ################################################################################################################################
# ################################################################################################################################

def apply_filter(expression:'str', data:'any_') -> 'FilterResult':
    """ Applies a JSONata expression to a value and returns the projection along with a full account of what happened.
    This is the runtime path and it never raises - a caller-supplied expression must not be able to crash the caller,
    so refusals and errors are captured in the result with the input passed through untouched. The input is never mutated.
    """

    # Our response to produce
    out = FilterResult()
    out.value = data
    out.size_before = get_size(data)
    out.size_after = out.size_before

    # Expressions over the length cap are refused before compilation is even attempted.
    expression_length = len(expression)
    is_too_long = expression_length > Max_Expression_Length

    if is_too_long:
        out.error = f'Expression too long: {expression_length} > {Max_Expression_Length}'
        out.error_kind = Kind_Too_Long
        return out

    # An expression that does not compile is a syntax error - captured, not raised.
    try:
        compiled = get_compiled(expression)
    except Exception as e:
        out.error = str(e)
        out.error_kind = Kind_Syntax_Error
        return out

    # An expression that compiles may still fail against this particular value - captured, not raised.
    try:
        result = compiled.evaluate(data)
    except Exception as e:
        out.error = str(e)
        out.error_kind = Kind_Evaluation_Error
        return out

    # JSONata yields None when nothing in the value matched the expression.
    out.value = result
    out.was_applied = True
    out.has_match = result is not None
    out.size_after = get_size(result)

    return out

# ################################################################################################################################
# ################################################################################################################################
