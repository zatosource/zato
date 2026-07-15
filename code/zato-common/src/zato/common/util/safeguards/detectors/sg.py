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

# The seven digits of an NRIC/FIN are weighted with these before the check letter is derived.
NRIC_Weights = [2, 7, 6, 5, 4, 3, 2]

# Check-letter tables per prefix family, indexed by the weighted sum modulo eleven.
NRIC_ST_Letters = 'JZIHGFEDCBA'
NRIC_FG_Letters = 'XWUTRQPNMLK'

# The T and G series add this to the weighted sum, the M series adds its own offset.
NRIC_TG_Offset = 4
NRIC_M_Offset  = 3

# ################################################################################################################################
# ################################################################################################################################

class NRICDetector(Detector):
    """ Singaporean NRIC/FIN - a prefix letter, seven digits and a check letter derived from a weighted sum.
    The S/T and F/G check-letter tables are publicly known, the M series table is not,
    so M numbers are accepted on shape alone.
    """
    name            = 'sg_nric'
    token           = 'SG_NRIC'
    region          = 'sg'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<![A-Za-z0-9])[STFGM]\d{7}[A-Z](?![A-Za-z0-9])', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        prefix = candidate[0]
        check_letter = candidate[8]

        # The seven digits are weighted and summed ..
        total = 0

        for weight, digit in zip(NRIC_Weights, candidate[1:8]):
            total += weight * int(digit)

        # .. the newer series in each prefix family add a fixed offset to the sum ..
        if prefix in ('T', 'G'):
            total += NRIC_TG_Offset
        elif prefix == 'M':
            total += NRIC_M_Offset

        remainder = total % 11

        # .. citizens and permanent residents use one published table ..
        if prefix in ('S', 'T'):
            out = check_letter == NRIC_ST_Letters[remainder]

        # .. the foreigner series uses another ..
        elif prefix in ('F', 'G'):
            out = check_letter == NRIC_FG_Letters[remainder]

        # .. and the M series table is not published, so its shape alone has to suffice.
        else:
            out = True

        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(NRICDetector())

# ################################################################################################################################
# ################################################################################################################################
