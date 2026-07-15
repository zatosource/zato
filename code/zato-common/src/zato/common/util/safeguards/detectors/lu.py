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
from stdnum import luhn as stdnum_luhn, verhoeff as stdnum_verhoeff

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class MatriculeDetector(Detector):
    """ Luxembourgish national identification number for natural persons - a YYYYMMDD birth date, three serial digits,
    a Luhn check digit over the first eleven and a Verhoeff check digit over the first twelve.
    """
    name            = 'lu_matricule'
    token           = 'LU_MATRICULE'
    region          = 'lu'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{5}(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':

        # The twelfth digit is a Luhn check over the first eleven ..
        first_twelve = candidate[:12]
        is_luhn_ok = stdnum_luhn.is_valid(first_twelve)

        if not is_luhn_ok:
            return False

        # .. and the thirteenth is a Verhoeff check over the first twelve.
        out = stdnum_verhoeff.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(MatriculeDetector())

# ################################################################################################################################
# ################################################################################################################################
