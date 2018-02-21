# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.sso.user import UserAPI

# ################################################################################################################################

class SSOAPI(object):
    """ An object through which user management and SSO-related functionality is accessed.
    """
    def __init__(self, sso_conf, odb_session_func, encrypt_func, decrypt_func, hash_func, new_user_id_func):
        self.sso_conf = sso_conf
        self.odb_session_func = odb_session_func
        self.encrypt_func = encrypt_func
        self.decrypt_func = decrypt_func
        self.hash_func = hash_func
        self.new_user_id_func = new_user_id_func
        self.encrypt_email = self.sso_conf.main.encrypt_email
        self.encrypt_password = self.sso_conf.main.encrypt_password
        self.password_expiry = self.sso_conf.password.expiry

        # User management, including passwords
        self.user = UserAPI(sso_conf, odb_session_func, encrypt_func, decrypt_func, hash_func, new_user_id_func)

# ################################################################################################################################
