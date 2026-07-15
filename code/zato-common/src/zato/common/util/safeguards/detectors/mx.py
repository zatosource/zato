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
from stdnum.mx import curp as stdnum_curp, rfc as stdnum_rfc

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class CURPDetector(Detector):
    """ Mexican population registry code - 18 characters of name letters, a birth date, sex, state,
    internal consonants, a differentiator and a check digit.
    """
    name            = 'mx_curp'
    token           = 'MX_CURP'
    region          = 'mx'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(
        r'(?<![A-Za-z0-9])[A-Z][AEIOUX][A-Z]{2}\d{6}[HMX][A-Z]{2}[B-DF-HJ-NP-TV-Z]{3}[A-Z0-9]\d(?![A-Za-z0-9])',
        ASCII,
    )

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_curp.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class RFCDetector(Detector):
    """ Mexican federal taxpayer registry code - three or four name letters, a six-digit date and a three-character
    homoclave, with structure and date checks but no reliably issued check digit.
    Codes containing the letter Enye are not matched - the detection engine is ASCII-only.
    """
    name            = 'mx_rfc'
    token           = 'MX_RFC'
    region          = 'mx'
    feasibility     = 'medium'
    default_enabled = False

    pattern = re_compile(r'(?<![A-Za-z0-9&])[A-Z&]{3,4}\d{6}[A-Z0-9]{3}(?![A-Za-z0-9])', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_rfc.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(CURPDetector())
register(RFCDetector())

# ################################################################################################################################
# ################################################################################################################################
