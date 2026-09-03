# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many milliseconds one second holds - used when converting callback durations
Ms_Per_Second = 1000

# Per-message trace diagnostics - opt-in through the environment because they log
# multiple lines per message, which is noise everywhere except a diagnostic run.
_is_trace_enabled = bool(os.environ.get('Zato_HL7_Trace'))

# ################################################################################################################################
# ################################################################################################################################

def trace(message:'str', *args:'object') -> 'None':
    """ Logs one per-message diagnostic line, when they are turned on.
    """
    if _is_trace_enabled:
        text = 'TRACE ' + message
        logger.info(text, *args)

# ################################################################################################################################
# ################################################################################################################################
