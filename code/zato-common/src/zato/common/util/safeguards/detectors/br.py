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
from stdnum.br import cnpj as stdnum_cnpj, cpf as stdnum_cpf

# ################################################################################################################################
# ################################################################################################################################

# Separators that may appear inside a written-out identifier.
Strip_Pattern = re_compile(r'[\s\-./]')

# ################################################################################################################################
# ################################################################################################################################

class CPFDetector(Detector):
    """ Brazilian individual taxpayer number - 11 digits with two mod-11 check digits, written NNN.NNN.NNN-NN or compact.
    """
    name            = 'br_cpf'
    token           = 'BR_CPF'
    region          = 'br'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_cpf.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class CNPJDetector(Detector):
    """ Brazilian legal-entity number - 14 digits with two mod-11 check digits, written NN.NNN.NNN/NNNN-NN or compact.
    """
    name            = 'br_cnpj'
    token           = 'BR_CNPJ'
    region          = 'br'
    feasibility     = 'high'
    default_enabled = True

    pattern = re_compile(r'(?<!\d)(?:\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14})(?!\d)', ASCII)

    def validate(self, candidate:'str') -> 'bool':
        out = stdnum_cnpj.is_valid(candidate)
        return out

# ################################################################################################################################

    def normalize(self, candidate:'str') -> 'str':
        out = Strip_Pattern.sub('', candidate)
        return out

# ################################################################################################################################
# ################################################################################################################################

class PassportDetector(Detector):
    """ Brazilian passport number - two letters followed by six digits, with no public checksum.
    """
    name            = 'br_passport'
    token           = 'BR_PASSPORT'
    region          = 'br'
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

register(CPFDetector())
register(CNPJDetector())
register(PassportDetector())

# ################################################################################################################################
# ################################################################################################################################
