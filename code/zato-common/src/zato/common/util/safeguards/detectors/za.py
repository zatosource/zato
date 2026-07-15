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
from stdnum.za import idnr as stdnum_idnr

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class IDNumberDetector(Detector):
    """ South African identity number - a YYMMDD birth date, a gender sequence, a citizenship digit
    and a Luhn check digit, 13 digits in all.
    """
    name            = 'za_id'
    token           = 'ZA_ID'
    region          = 'za'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)\d{13}(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_idnr.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PassportDetector(Detector):
    """ South African passport number - one letter followed by eight digits, with no public checksum.
    """
    name            = 'za_passport'
    token           = 'ZA_PASSPORT'
    region          = 'za'
    feasibility     = 'medium'
    default_enabled = False

    pattern = re_compile(r'(?<![A-Za-z0-9])[A-Z]\d{8}(?![A-Za-z0-9])', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        # The pattern alone defines this format - there is no checksum to confirm.
        return True

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(IDNumberDetector())
register(PassportDetector())

# ################################################################################################################################
# ################################################################################################################################
