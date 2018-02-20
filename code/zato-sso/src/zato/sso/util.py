# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from uuid import uuid4

# Base32 Crockford
from base32_crockford import encode as crockford_encode

# Zato
from zato.sso import status_code, ValidationError

# ################################################################################################################################

def _new_id(prefix, _uuid4=uuid4, _crockford_encode=crockford_encode):
    return '%s%s' % (prefix, _crockford_encode(_uuid4().int).lower())

# ################################################################################################################################

def new_confirm_token(_new_id=_new_id):
    return _new_id('zcnt')

# ################################################################################################################################

def new_user_id(_new_id=_new_id):
    return _new_id('zusr')

# ################################################################################################################################

def validate_password(sso_conf, password):
    """ Raises ValidationError if password is invalid, e.g. it is too simple.
    """
    # Password may not be too short
    if len(password) < sso_conf.password.min_length:
        raise ValidationError(status_code.password.too_short, sso_conf.password.inform_if_invalid)

    # Password may not be too long
    if len(password) > sso_conf.password.max_length:
        raise ValidationError(status_code.password.too_long, sso_conf.password.inform_if_invalid)

    # Password's default complexity is checked case-insensitively
    password = password.lower()

    # Password may not contain most commonly used ones
    for elem in sso_conf.password.reject_list:
        if elem in password:
            raise ValidationError(status_code.password.invalid, sso_conf.password.inform_if_invalid)

# ################################################################################################################################

def make_data_secret(data, encrypt_func=None, hash_func=None):
    """ Turns data into a secret by hashing it (stretching) and then encrypting the result.
    """
    # E.g. PBKDF2-SHA512
    if hash_func:
        data = hash_func(data)

    # E.g. Fernet (AES-128)
    if encrypt_func:
        data = encrypt_func(data)

    return data

# ################################################################################################################################

def make_password_secret(password, encrypt_password, encrypt_func=None, hash_func=None):
    """ Encrypts and hashes a user password.
    """
    return make_data_secret(password, encrypt_func if encrypt_password else None, hash_func)

# ################################################################################################################################
