# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class CacheConfig:
    """ The cached channels of the response cache suite and the file in which the cached service records its invocations.
    """

    # The variable with the path of the file that receives one line for each invocation of the cached service,
    # which every worker appends to, so the file counts the invocations of all the workers together
    Invocation_Log_Env = 'Zato_Test_Multi_CPU_Invocation_Log'

    # How long the cached service runs, in seconds, which keeps an invocation in progress while a test acts
    Service_Duration = 3.0

    Cached_Service = 'test.multi-cpu.cached-slow'
    Invalidate_Service = 'test.multi-cpu.invalidate-response'

    # The channel that caches on the first request and the one that caches on the second request
    First_Channel_Name = 'test.multi-cpu.cache.first'
    First_Channel_Path = '/test/multi-cpu/cache/first'

    Second_Channel_Name = 'test.multi-cpu.cache.second'
    Second_Channel_Path = '/test/multi-cpu/cache/second'

# ################################################################################################################################
# ################################################################################################################################
