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
from stdnum.nz import ird as stdnum_ird

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# The NHI alphabet excludes I and O, each letter mapping to its one-based position here.
NHI_Letters = 'ABCDEFGHJKLMNPQRSTUVWXYZ'

# The NHI check digit weights the three letter ordinals and the three digits that follow them.
NHI_Weights = [7, 6, 5, 4, 3, 2]

# ################################################################################################################################
# ################################################################################################################################

class IRDDetector(Detector):
    """ New Zealand tax number - 8 or 9 digits in a bounded range with a two-stage weighted mod-11 check digit,
    often written in groups of two or three.
    """
    name            = 'nz_ird'
    token           = 'NZ_IRD'
    region          = 'nz'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)(?:\d{2,3}[ -]\d{3}[ -]\d{3}|\d{8,9})(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_ird.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class NHIDetector(Detector):
    """ New Zealand national health index number - three letters excluding I and O, then either three digits
    and a mod-11 check digit, or, since 2019, two digits and two letters with an unpublished check algorithm.
    """
    name            = 'nz_nhi'
    token           = 'NZ_NHI'
    region          = 'nz'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<![A-Za-z0-9])[A-HJ-NP-Z]{3}\d{2}(?:\d{2}|[A-HJ-NP-Z]{2})(?![A-Za-z0-9])', ASCII)

    def validate(self, candidate:'str') -> 'bool':

        # The sixth character tells the formats apart - only the all-digit one carries a published checksum ..
        sixth = candidate[5]
        is_checksummed = sixth.isdigit()

        # .. the 2019 format's check algorithm is not public, so its shape alone has to suffice.
        if not is_checksummed:
            return True

        # Letters map to their one-based ordinals with I and O excluded, digits count as themselves ..
        values = []

        for letter in candidate[:3]:
            ordinal = NHI_Letters.index(letter) + 1
            values.append(ordinal)

        for digit in candidate[3:6]:
            values.append(int(digit))

        # .. the weighted sum modulo eleven produces the check digit ..
        total = 0

        for weight, value in zip(NHI_Weights, values):
            total += weight * value

        remainder = total % 11
        check = (11 - remainder) % 11

        # .. a result of ten can never be encoded, so such numbers are invalid.
        if check == 10:
            return False

        check_digit = candidate[6]

        out = check == int(check_digit)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(IRDDetector())
register(NHIDetector())

# ################################################################################################################################
# ################################################################################################################################
