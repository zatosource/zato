# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The date ranges the audit log reports run over.

from __future__ import annotations

# stdlib
from datetime import datetime, timedelta

# Zato
from zato.common.audit_log.api import Retention_Days

# ################################################################################################################################
# ################################################################################################################################

# The selectable report ranges
Range_Day   = 'day'
Range_Week  = 'week'
Range_Month = 'month'

# How far back each range reaches - the widest one is the audit log's own retention window,
# so the report never claims to cover more than the log actually holds.
Range_Hours = {
    Range_Day:   24,
    Range_Week:  7 * 24,
    Range_Month: Retention_Days * 24,
}

# The range a page opens with when none was chosen
Default_Range = Range_Week

# ################################################################################################################################
# ################################################################################################################################

def get_range_cutoff(now:'datetime', time_range:'str') -> 'str':
    """ Returns the ISO timestamp the given range reaches back to.
    """
    range_hours = Range_Hours[time_range]
    cutoff = now - timedelta(hours=range_hours)

    out = cutoff.isoformat()
    return out

# ################################################################################################################################
# ################################################################################################################################
