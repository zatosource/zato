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
        invalid  = 'zsv.usr.001'
        exists   = 'zsv.usr.002'
        too_long = 'zsv.usr.003'

    class email:
        exists   = 'zsv.email.002'
        email_too_long = 'zsv.email.003'

    class password:
        invalid  = 'zsv.passwd.001'
        too_long = 'zsv.passwd.003'
        has_ws   = 'zsv.passwd.004'

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
    """ A business-level user, e.g. a person on whose behalf a given service runs.
    """

# ################################################################################################################################

