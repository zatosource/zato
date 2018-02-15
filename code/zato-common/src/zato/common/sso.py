# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

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

class User(object):
    """ An SSO user and related attributes.
    """
    def __init__(self):
        self.user_id = None
        self.is_active = None
        self.is_internal = None
        self.is_locked = None
        self.locked_time = None
        self.locked_by = None
        self.username = None
        self.password = None
        self.password_is_set = None
        self.password_must_change = None
        self.password_expiry = None
        self.sign_up_status = None
        self.sign_up_time = None
        self.sign_up_confirm_time = None
        self.email = None
        self.display_name = None
        self.first_name = None
        self.middle_name = None
        self.last_name = None
        self.display_name_upper = None
        self.first_name_upper = None
        self.middle_name_upper = None
        self.last_name_upper = None

    @staticmethod
    def signup(session, input):
        user = User()
        print(user)

# ################################################################################################################################

