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
from stdnum.ca import sin as stdnum_sin

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# ################################################################################################################################
# ################################################################################################################################

class SINDetector(Detector):
    """ Canadian social insurance number - 9 digits validated with the Luhn algorithm, written in groups of three
    or as one compact run, never starting with 0 or 8.
    """
    name            = 'ca_sin'
    token           = 'CA_SIN'
    region          = 'ca'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)(?:\d{3}[ -]\d{3}[ -]\d{3}|\d{9})(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_sin.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PassportDetector(Detector):
    """ Canadian passport number - two letters followed by six digits, with no public checksum.
    """
    name            = 'ca_passport'
    token           = 'CA_PASSPORT'
    region          = 'ca'
    feasibility     = 'medium'
    default_enabled = False

    pattern = re_compile(r'(?<![A-Za-z0-9])[A-Z]{2}\d{6}(?![A-Za-z0-9])', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        # The pattern alone defines this format - there is no checksum to confirm.
        return True

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(SINDetector())
register(PassportDetector())

# ################################################################################################################################
# ################################################################################################################################
