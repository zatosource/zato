# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from re import ASCII, compile as re_compile

# piigex
from piigex.detectors import register
from piigex.detectors.base import Detector

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class PassportDetector(Detector):
    """ Finnish passport number - two letters followed by seven digits, with no public checksum.
    """
    name            = 'fi_passport'
    token           = 'FI_PASSPORT'
    region          = 'fi'
    feasibility     = 'medium'
    default_enabled = False

    pattern = re_compile(r'(?<![A-Za-z0-9])[A-Z]{2}\d{7}(?![A-Za-z0-9])', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        # The pattern alone defines this format - there is no checksum to confirm.
        return True

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(PassportDetector())

# ################################################################################################################################
# ################################################################################################################################
