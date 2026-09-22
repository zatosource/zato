# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The environment variable every system's password comes from
Password_Env = 'Zato_Password'

# ################################################################################################################################
# ################################################################################################################################

class PasswordRules(NamedTuple):
    min_length: int
    needs_upper: bool
    needs_lower: bool
    needs_digit: bool
    needs_symbol: bool

# ################################################################################################################################
# ################################################################################################################################

# Systems with no rules of their own take the plain value
No_Rules = PasswordRules(0, False, False, False, False)

# What is appended for each missing character class
_class_suffixes = {
    'upper':  'Z',
    'lower':  'z',
    'digit':  '7',
    'symbol': '!',
}

# ################################################################################################################################
# ################################################################################################################################

def get_password() -> 'str':
    """ Returns the password from the environment, failing when it is unset.
    """
    if out := os.environ.get(Password_Env):
        return out
    else:
        raise Exception(f'{Password_Env} is not set - export it before starting any live HL7 system')

# ################################################################################################################################

def _missing_classes(password:'str', rules:'PasswordRules') -> 'strlist':
    """ Names the character classes the rules want and the password lacks.
    """
    out:'strlist' = []

    has_upper  = False
    has_lower  = False
    has_digit  = False
    has_symbol = False

    for character in password:
        if character.isupper():
            has_upper = True
        if character.islower():
            has_lower = True
        if character.isdigit():
            has_digit = True
        if not character.isalnum():
            has_symbol = True

    if rules.needs_upper:
        if not has_upper:
            out.append('upper')

    if rules.needs_lower:
        if not has_lower:
            out.append('lower')

    if rules.needs_digit:
        if not has_digit:
            out.append('digit')

    if rules.needs_symbol:
        if not has_symbol:
            out.append('symbol')

    return out

# ################################################################################################################################

def password_for(rules:'PasswordRules') -> 'str':
    """ Returns the password a system is given. Some systems have rules the plain value may not meet,
    and for those the value is extended until it does.
    """
    password = get_password()

    # Add what is missing, class by class ..
    out = password

    for class_name in _missing_classes(password, rules):
        out += _class_suffixes[class_name]

    # .. and pad to the minimum length with the last suffix character, which keeps every class present.
    while len(out) < rules.min_length:
        out += out[-1]

    return out

# ################################################################################################################################
# ################################################################################################################################
