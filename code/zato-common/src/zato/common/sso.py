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
from zato.common.util.sso import new_user_id

# ################################################################################################################################

_utcnow = datetime.utcnow

# ################################################################################################################################

class reason_code:
    """ Reason codes pointing to specific API validation errors.
    """
    class username:
        invalid        = 'zsv.usr.001'
        exists         = 'zsv.usr.002'
        too_long       = 'zsv.usr.003'
        has_whitespace = 'zsv.usr.004'

    class email:
        invalid        = 'zsv.email.001'
        exists         = 'zsv.email.002'
        too_long       = 'zsv.email.003'
        has_whitespace = 'zsv.email.004'
        missing        = 'zsv.email.005'

    class password:
        invalid   = 'zsv.passwd.001'
        too_short = 'zsv.passwd.002'
        too_long  = 'zsv.passwd.003'

    class app_list:
        invalid   = 'zsi.appl.001'
        no_signup = 'zsi.appl.002'

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
    def __init__(self, reason_code, return_rc):
        self.reason_code = reason_code if isinstance(reason_code, list) else [reason_code]
        self.return_rc = return_rc

# ################################################################################################################################

def create_user(session, input, is_approval_needed, password_expiry, encrypt_password, encrypt_email, encrypt_func,
    hash_func, _utcnow=_utcnow, _timedelta=timedelta):

    # Always in UTC
    now = _utcnow()

    # Normalize input
    input.display_name = input.display_name.strip()
    input.first_name = input.first_name.strip()
    input.middle_name = input.middle_name.strip()
    input.last_name = input.last_name.strip()

    # If display_name is given on input, this will be the final value of that attribute ..
    if input.display_name:
        display_name = input.display_name.strip()

    # .. otherwise, display_name is a concatenation of first, middle and last name.
    else:
        display_name = ''

        if input.first_name:
            display_name += input.first_name
            display_name += ' '

        if input.middle_name:
            display_name += input.middle_name
            display_name += ' '

        if input.last_name:
            display_name += input.last_name

        display_name = display_name.strip()

    user_model = UserModel()
    user_model.user_id = new_user_id()
    user_model.is_active = True
    user_model.is_internal = True
    user_model.is_approved = False if is_approval_needed else True
    user_model.is_locked = False
    user_model.is_super_user = False

    # E.g. PBKDF2-SHA512
    password = hash_func(input.password)

    # Fernet (AES-128)
    if encrypt_password:
        password = encrypt_func(password)

    # Again, Fernet key
    email = encrypt_func(input.email) if encrypt_email else input.email

    user_model.username = input.username
    user_model.email = email
    user_model.password = password
    user_model.password_is_set = True
    user_model.password_must_change = False
    user_model.password_expiry = now + timedelta(days=password_expiry)

    user_model.sign_up_status = const.signup_status.before_confirmation
    user_model.sign_up_time = now

    user_model.display_name = display_name
    user_model.first_name = input.first_name
    user_model.middle_name = input.middle_name
    user_model.last_name = input.last_name

    # Uppercase any and all names for indexing purposes.
    user_model.display_name_upper = display_name.upper()
    user_model.first_name_upper = input.first_name.upper()
    user_model.middle_name_upper = input.middle_name.upper()
    user_model.last_name_upper = input.last_name.upper()

    return user_model

# ################################################################################################################################
