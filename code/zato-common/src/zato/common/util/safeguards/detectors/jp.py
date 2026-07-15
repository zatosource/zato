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
from stdnum.jp import cn as stdnum_cn, in_ as stdnum_individual

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class MyNumberDetector(Detector):
    """ Japanese individual number - 12 digits whose last one is a mod-11 check digit, often written in groups of four.
    """
    name            = 'jp_my_number'
    token           = 'JP_MY_NUMBER'
    region          = 'jp'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_individual.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class CorporateNumberDetector(Detector):
    """ Japanese corporate number - 13 digits whose first one is a mod-9 check digit over the remaining twelve.
    """
    name            = 'jp_corporate_number'
    token           = 'JP_CORPORATE_NUMBER'
    region          = 'jp'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)[1-9]\d{12}(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_cn.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PassportDetector(Detector):
    """ Japanese passport number - two letters followed by seven digits, with no public checksum.
    """
    name            = 'jp_passport'
    token           = 'JP_PASSPORT'
    region          = 'jp'
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

register(MyNumberDetector())
register(CorporateNumberDetector())
register(PassportDetector())

# ################################################################################################################################
# ################################################################################################################################
