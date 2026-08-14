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
from stdnum import imei as stdnum_imei

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class IMEIDetector(Detector):
    """ International mobile equipment identity (IMEI) - 15 digits with a Luhn check digit, written as one compact run
    or in 2-6-6-1 groups separated by spaces or dashes.
    """
    name            = 'intl_imei'
    token           = 'INTL_IMEI'
    region          = 'intl'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)(?:\d{2}[ -]\d{6}[ -]\d{6}[ -]\d|\d{15})(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_imei.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(IMEIDetector())

# ################################################################################################################################
# ################################################################################################################################
