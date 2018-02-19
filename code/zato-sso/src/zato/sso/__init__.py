# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime, timedelta

# Zato
from zato.common.odb.model import SSOUser as UserModel

# ################################################################################################################################

_utcnow = datetime.utcnow

UserModelTable = UserModel.__table__

# ################################################################################################################################

class status_code:
    """ Reason codes pointing to specific API validation errors.
    """
    ok       = 'ok'
    error    = 'error'
    warning  = 'warning'

    class username:
        invalid        = 'E001001'
        exists         = 'E001002'
        too_long       = 'E001003'
        has_whitespace = 'E001004'

    class email:
        invalid        = 'E002001'
        exists         = 'E002002'
        too_long       = 'E002003'
        has_whitespace = 'E002004'
        missing        = 'E002005'

    class password:
        invalid   = 'E003001'
        too_short = 'E003002'
        too_long  = 'E003003'

        expired        = 'E003004'
        w_about_to_exp = 'W003005'
        e_about_to_exp = 'E003006'
        must_send_new  = 'E003007'

    class app_list:
        invalid   = 'E004001'
        no_signup = 'E004002'

    class auth:
        not_allowed           = 'E005001' # Generic 'You are not allowed to access this resource'
        locked                = 'E005002'
        invalid_signup_status = 'E005003'
        not_approved          = 'E005004'

    class metadata:
        not_allowed = 'E006001'

# ################################################################################################################################

class const:
    """ Constants used in SSO.
    """
    class signup_status:
        before_confirmation = 'before_confirmation'
        to_approve          = 'to_approve'
        final               = 'final'

# ################################################################################################################################

class ValidationError(Exception):
    """ Raised if any input SSO data is invalid, subcode contains details of what was rejected.
    """
    def __init__(self, sub_status, return_status, status=status_code.error):
        self.sub_status = sub_status if isinstance(sub_status, list) else [sub_status]
        self.return_status = return_status
        self.status = status

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
