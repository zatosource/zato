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

# stdnum
from stdnum.in_ import aadhaar as stdnum_aadhaar, pan as stdnum_pan

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class AadhaarDetector(Detector):
    """ Indian resident identity number - 12 digits starting with 2-9, the last one a Verhoeff check digit,
    often written in groups of four.
    """
    name            = 'in_aadhaar'
    token           = 'IN_AADHAAR'
    region          = 'in'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)[2-9]\d{3}[ -]?\d{4}[ -]?\d{4}(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_aadhaar.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PANDetector(Detector):
    """ Indian permanent account number - five letters, four digits and a final letter, with holder-type
    and name-letter structure but no arithmetic check digit.
    """
    name            = 'in_pan'
    token           = 'IN_PAN'
    region          = 'in'
    feasibility     = 'medium'
    default_enabled = False

    pattern = re_compile(r'(?<![A-Za-z0-9])[A-Z]{5}\d{4}[A-Z](?![A-Za-z0-9])', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_pan.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PassportDetector(Detector):
    """ Indian passport number - one letter followed by seven digits, with no public checksum.
    """
    name            = 'in_passport'
    token           = 'IN_PASSPORT'
    region          = 'in'
    feasibility     = 'medium'
    default_enabled = False

    pattern = re_compile(r'(?<![A-Za-z0-9])[A-Z]\d{7}(?![A-Za-z0-9])', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        # The pattern alone defines this format - there is no checksum to confirm.
        return True

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(AadhaarDetector())
register(PANDetector())
register(PassportDetector())

# ################################################################################################################################
# ################################################################################################################################
