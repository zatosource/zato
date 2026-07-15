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
from stdnum.au import abn as stdnum_abn, tfn as stdnum_tfn

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-]')

# The Medicare check digit is a weighted sum of the first eight digits, modulo ten.
Medicare_Weights = [1, 3, 7, 9, 1, 3, 7, 9]

# ################################################################################################################################
# ################################################################################################################################

class TFNDetector(Detector):
    """ Australian tax file number - 8 or 9 digits with a weighted mod-11 checksum, often written in groups of three.
    """
    name            = 'au_tfn'
    token           = 'AU_TFN'
    region          = 'au'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)(?:\d{3}[ -]\d{3}[ -]\d{2,3}|\d{8,9})(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_tfn.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class ABNDetector(Detector):
    """ Australian business number - 11 digits whose two leading check digits use a mod-89 algorithm, never starting with zero.
    """
    name            = 'au_abn'
    token           = 'AU_ABN'
    region          = 'au'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)(?:\d{2}[ -]\d{3}[ -]\d{3}[ -]\d{3}|[1-9]\d{10})(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_abn.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class MedicareDetector(Detector):
    """ Australian Medicare card number - 10 digits, the first between 2 and 6, the ninth a weighted check digit
    and the tenth a card issue number that is never zero.
    """
    name            = 'au_medicare'
    token           = 'AU_MEDICARE'
    region          = 'au'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)[2-6]\d{3}[ -]?\d{5}[ -]?\d(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        digits = Strip_Pattern.sub('', candidate)
        first_eight = digits[:8]

        # The ninth digit is a weighted checksum of the first eight ..
        total = 0

        for weight, digit in zip(Medicare_Weights, first_eight):
            total += weight * int(digit)

        check = total % 10
        check_digit = digits[8]

        if check != int(check_digit):
            return False

        # .. and the tenth, the card issue number, is never zero.
        issue_digit = digits[9]

        out = issue_digit != '0'
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PassportDetector(Detector):
    """ Australian passport number - one or two letters followed by seven digits, with no public checksum.
    """
    name            = 'au_passport'
    token           = 'AU_PASSPORT'
    region          = 'au'
    feasibility     = 'medium'
    default_enabled = False

    pattern = re_compile(r'(?<![A-Za-z0-9])[A-Z]{1,2}\d{7}(?![A-Za-z0-9])', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        # The pattern alone defines this format - there is no checksum to confirm.
        return True

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

register(TFNDetector())
register(ABNDetector())
register(MedicareDetector())
register(PassportDetector())

# ################################################################################################################################
# ################################################################################################################################
