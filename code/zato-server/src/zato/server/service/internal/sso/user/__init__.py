# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.sso import new_confirm_token
from zato.server.service import List, Service

# ################################################################################################################################

class status_subcode:
    username_invalid   = 'zsi.001.001'
    username_exists    = 'zsi.001.002'
    username_too_long  = 'zsi.001.003'
    email_exists       = 'zsi.002.002'
    email_too_long     = 'zsi.002.003'
    password_invalid   = 'zsi.003.001'
    password_too_long  = 'zsi.003.003'
    password_has_ws    = 'zsi.003.004'
    app_list_invalid   = 'zsi.004.001'
    app_list_no_signup = 'zsi.004.002'

# ################################################################################################################################

class Validate(Service):
    """ Validates creation of user data in accordance with configuration from sso.conf.
    """
    class SimpleIO:
        input_required = ('username', 'email', 'password', List('app_list'))
        output_required = ('is_valid',)
        output_optional = ('status_subcode',)
        encrypt_secrets = False
        response_elem = None

    def _validate_username(self, username):
        """ Raises ValidationError if username is invalid.
        """

    def _validate_email(self, email):
        """ Raises ValidationError if email is invalid.
        """

    def _validate_password(self, password):
        """ Raises ValidationError if password is invalid.
        """

    def _validate_app_list(self, password):
        """ Raises ValidationError if password is invalid.
        """

    def handle(self):
        self.logger.info(self.request.input)
        self.response.payload.is_valid = True

# ################################################################################################################################
