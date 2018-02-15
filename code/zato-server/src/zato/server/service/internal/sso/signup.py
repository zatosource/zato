# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.sso import create_user
from zato.common.util.sso import new_confirm_token
from zato.server.service import List, Service

# ################################################################################################################################

class Signup(Service):
    """ Lets users sign up with the system.
    """
    class SimpleIO:
        input_required = ('username', 'password', 'current_app', List('app_list'))
        input_optional = ('email', 'display_name', 'first_name', 'middle_name', 'last_name')
        output_optional = ('confirm_token', List('reason_code'),)
        encrypt_secrets = False
        response_elem = None
        skip_empty_keys = True

# ################################################################################################################################

    def handle_POST(self):

        # Local aliases
        input = self.request.input
        sso_conf = self.server.sso_config

        # By default, this is always returned, no matter if successful or not, to prevent exploitation
        # by attackers trying to find out if a given user/email exists or not.
        if sso_conf.signup.return_confirm_token:
            self.response.payload.confirm_token = new_confirm_token()

        # Always lower-cased so as to be treated in a uniform manner
        input.username = input.username.lower()
        input.email = input.get('email', '').lower()

        for name in sso_conf.user_validation.service:
            validation_response = self.invoke(name, {
                'username': input.username,
                'email': input.email,
                'password': input.password,
                'current_app': input.current_app,
                'app_list': input.app_list,
            }, as_bunch=True)

            if not validation_response.is_valid:
                # Reason code list is returned only if validation failed and it was confirmed that we are safe to return it
                # so we can just assign it to payload unconditionally.
                self.response.payload.reason_code = validation_response.reason_code
                return

        # None of validation services returned an error so we can create the user now
        with closing(self.odb.session()) as session:
            user = create_user(session, input, sso_conf.signup.is_approval_needed, sso_conf.signup.password_expiry,
                sso_conf.main.encrypt_password, sso_conf.main.encrypt_email, self.server.encrypt, self.server.hash_secret)
            session.add(user)
            session.commit()

        # Invoke any callback services configured

# ################################################################################################################################
