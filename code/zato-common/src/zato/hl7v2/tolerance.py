# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from zato.hl7v2_rs import ToleranceConfig, apply_tolerance as _apply_tolerance

# ################################################################################################################################
# ################################################################################################################################

def _apply_tolerance_impl(raw:'str', tolerance:'ToleranceConfig') -> 'str':
    return _apply_tolerance(raw, tolerance)  # type: ignore[no-any-return]

# ################################################################################################################################
# ################################################################################################################################
