# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import hashlib
from json import dumps
from time import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, float_, int_, strdict

# ################################################################################################################################
# ################################################################################################################################

class CacheStats:
    """ Track cache statistics.
    """

    def __init__(self) -> 'None':
        self.hits = 0
        self.misses = 0
        self.total_time = 0.0
        self.start_time = 0.0

    def start(self) -> 'None':
        """ Start timing an operation.
        """
        self.start_time = time()

    def stop(self) -> 'None':
        """ Stop timing an operation.
        """
        if self.start_time:
            self.total_time += time() - self.start_time
            self.start_time = 0.0

    def hit(self) -> 'None':
        """ Record a cache hit.
        """
        self.hits += 1

    def miss(self) -> 'None':
        """ Record a cache miss.
        """
        self.misses += 1

    @property
    def total(self) -> 'int_':
        """ Get the total number of cache operations.
        """
        return self.hits + self.misses

    @property
    def hit_ratio(self) -> 'float_':
        """ Get the cache hit ratio.
        """
        if self.total == 0:
            return 0.0
        return self.hits / self.total

    def reset(self) -> 'None':
        """ Reset all statistics.
        """
        self.hits = 0
        self.misses = 0
        self.total_time = 0.0
        self.start_time = 0.0

# ################################################################################################################################
# ################################################################################################################################

class CacheKey:
    """ Utility functions for generating cache keys.
    """

    @staticmethod
    def for_expression(expression:'any_') -> 'str':
        """ Generate a cache key for an expression.
        """
        return str(expression)

    @staticmethod
    def for_rule(rule_name:'str', data:'strdict') -> 'str':
        """ Generate a cache key for a rule and data combination.
        """
        # Sort keys to ensure consistent ordering
        serialized = dumps(data, sort_keys=True, default=str)

        # Use SHA-1 for better security and distribution
        data_hash = hashlib.sha1(serialized.encode('utf-8')).hexdigest()
        return f'{rule_name}:{data_hash}'

# ################################################################################################################################
# ################################################################################################################################

def timed_execution(func:'callable_', *args:'any_', **kwargs:'any_') -> 'tuple[any_, float_]':
    """ Execute a function and measure its execution time.
    """
    start_time = time()
    result = func(*args, **kwargs)
    execution_time = time() - start_time
    return result, execution_time

# ################################################################################################################################
# ################################################################################################################################
