# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# How far below the delay it waits for a duration that a test measures may fall. The delay starts on a clock other than
# the one the test reads, in another thread, greenlet or process, and timers end at the granularity of the system clock.
Timer_Tolerance_Seconds = 0.1
Timer_Tolerance_Ms = 100

# ################################################################################################################################
# ################################################################################################################################
