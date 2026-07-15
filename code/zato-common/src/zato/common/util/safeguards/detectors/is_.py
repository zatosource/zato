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
from stdnum.is_ import kennitala as stdnum_kennitala

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class KennitalaDetector(Detector):
    """ Icelandic identity number for people and organisations - a birth date, two serial digits,
    a weighted mod-11 check digit and a century digit, written DDMMYY-NNNC or compact.
    """
    name            = 'is_kennitala'
    token           = 'IS_KENNITALA'
    region          = 'is'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)\d{6}-?\d{4}(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_kennitala.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(KennitalaDetector())

# ################################################################################################################################
# ################################################################################################################################
