# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# ################################################################################################################################
# ################################################################################################################################

def utc_now() -> 'datetime':
    """ Returns a timezone-neutral UTC value for identical behavior across all supported databases.
    """
    # Read an aware UTC value ..
    current = datetime.now(timezone.utc)

    # .. and remove timezone metadata because every supported database preserves a naive UTC value identically.
    out = current.replace(tzinfo=None)
    return out

# ################################################################################################################################
# ################################################################################################################################
