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

# ################################################################################################################################
# ################################################################################################################################

class PSNDetector(Detector):
    """ Philippine PhilSys number - 12 random digits with no public checksum, written in groups of four.
    Any 12-digit run matches the shape, so this detector never runs unless it is picked by name.
    """
    name            = 'ph_psn'
    token           = 'PH_PSN'
    region          = 'ph'
    feasibility     = 'low'
    default_enabled = False

    pattern = re_compile(r'(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        # The pattern alone defines this format - there is no checksum to confirm.
        return True

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PCNDetector(Detector):
    """ Philippine PhilSys card number - 16 digits derived from the PhilSys number, with no public checksum,
    written in groups of four. Any 16-digit run matches the shape, so this detector never runs
    unless it is picked by name.
    """
    name            = 'ph_pcn'
    token           = 'PH_PCN'
    region          = 'ph'
    feasibility     = 'low'
    default_enabled = False

    pattern = re_compile(r'(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        # The pattern alone defines this format - there is no checksum to confirm.
        return True

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(PSNDetector())
register(PCNDetector())

# ################################################################################################################################
# ################################################################################################################################
