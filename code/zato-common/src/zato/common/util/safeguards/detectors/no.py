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
from stdnum.no import fodselsnummer as stdnum_fodselsnummer

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class FodselsnummerDetector(Detector):
    """ Norwegian national identity number - a DDMMYY birth date, a three-digit individual number
    and two weighted mod-11 check digits.
    """
    name            = 'no_fnr'
    token           = 'NO_FNR'
    region          = 'no'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)\d{11}(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_fodselsnummer.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(FodselsnummerDetector())

# ################################################################################################################################
# ################################################################################################################################
