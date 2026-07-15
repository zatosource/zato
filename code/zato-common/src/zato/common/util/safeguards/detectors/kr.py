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
from stdnum.kr import rrn as stdnum_rrn

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class RRNDetector(Detector):
    """ South Korean resident registration number - a birth date, a sex-and-century digit, a birthplace code,
    a serial and a mod-11 check digit, written YYMMDD-NNNNNNN or compact.
    """
    name            = 'kr_rrn'
    token           = 'KR_RRN'
    region          = 'kr'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)\d{6}[ -]?\d{7}(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_rrn.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PassportDetector(Detector):
    """ South Korean passport number - the letter M or S followed by eight digits, with no public checksum.
    """
    name            = 'kr_passport'
    token           = 'KR_PASSPORT'
    region          = 'kr'
    feasibility     = 'medium'
    default_enabled = False

    pattern = re_compile(r'(?<![A-Za-z0-9])[MS]\d{8}(?![A-Za-z0-9])', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        # The pattern alone defines this format - there is no checksum to confirm.
        return True

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(RRNDetector())
register(PassportDetector())

# ################################################################################################################################
# ################################################################################################################################
