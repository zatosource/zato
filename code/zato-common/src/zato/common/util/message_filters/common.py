# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Maximum length of a filter expression in characters - longer ones are refused before compilation.
Max_Expression_Length = 10_000

# At most this many compiled expressions are kept in the cache.
Max_Cache_Entries = 1_000

# Kinds of errors that can appear in a result.
Kind_Too_Long         = 'too_long'
Kind_Syntax_Error     = 'syntax_error'
Kind_Evaluation_Error = 'evaluation_error'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FilterResult:
    """ The outcome of applying a filter expression to a value - the projected value plus a full account of what happened.
    """
    value: any_
    was_applied: bool = False
    has_match:   bool = False
    error:       str = ''
    error_kind:  str = ''
    size_before: int = 0
    size_after:  int = 0

# ################################################################################################################################
# ################################################################################################################################
