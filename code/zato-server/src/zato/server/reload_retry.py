# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The delays with which the worker and the config process of a server reload their configuration again after a reload
# that failed, e.g. while the Zato database cannot be reached, until a reload succeeds.

# ################################################################################################################################
# ################################################################################################################################

# How long a process waits before its first reload after a failed one, in seconds
Reload_Retry_Initial_Seconds = 1.0

# How much the delay grows after each failed reload, and the upper limit of the delay, in seconds
Reload_Retry_Factor = 2.0
Reload_Retry_Max_Seconds = 30.0

# ################################################################################################################################
# ################################################################################################################################

def next_reload_retry_delay(delay:'float') -> 'float':
    """ Returns the delay before the reload that follows a reload which failed after the given delay.
    """
    grown = delay * Reload_Retry_Factor
    out = min(grown, Reload_Retry_Max_Seconds)
    return out

# ################################################################################################################################
# ################################################################################################################################
