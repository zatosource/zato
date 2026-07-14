# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# jsonata-python
from jsonata import Jsonata

# Zato
from zato.common.util.message_filters.common import Max_Cache_Entries

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
str_jsonata_dict = dict[str, Jsonata]

# ################################################################################################################################
# ################################################################################################################################

# Compiled expressions keyed by their source text - dicts preserve insertion order,
# which the eviction below relies on to drop the oldest entry first.
_cache:'str_jsonata_dict' = {}

# ################################################################################################################################
# ################################################################################################################################

def get_compiled(expression:'str') -> 'Jsonata':
    """ Returns a compiled JSONata expression, reusing a previously compiled one when possible.
    Compiling is the expensive step and the same expression tends to be applied over and over,
    so each expression is compiled once and kept for later calls.
    """

    # A cache hit skips compilation entirely.
    if out := _cache.get(expression):
        return out

    # Compilation happens before the cache is touched, so an expression that fails to compile is never cached.
    out = Jsonata(expression)

    # The oldest entry makes room when the cache is full.
    cache_size = len(_cache)
    is_full = cache_size >= Max_Cache_Entries

    if is_full:
        oldest = next(iter(_cache))
        del _cache[oldest]

    _cache[expression] = out

    return out

# ################################################################################################################################
# ################################################################################################################################
