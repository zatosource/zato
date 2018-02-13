# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.sso import new_confirm_token
from zato.server.service import List, Service

# ################################################################################################################################

class SignUp(Service):
    """ Lets users sign up with the system.
    """
    class SimpleIO:
        input_required = ('username', 'password', List('app_list'))
        input_optional = ('email', 'display_name', 'first_name', 'middle_name', 'last_name')
        output_required = ('confirm_token',)
        encrypt_secrets = False
        response_elem = None

    def handle_POST(self):

        # By default, this is always returned, no matter if successful or not, to prevent exploitation
        # by attackers trying to find out if a given user/email exists or not.
        confirm_token = new_confirm_token()

        # Local shortcuts
        input = self.request.input

        validation_response = self.invoke(Validate.get_name(), {
            'username': input.username,
            'email': input.email,
            'password': input.password,
            'app_list': input.app_list,
        })

        self.logger.info(validation_response)

        self.response.payload.confirm_token = confirm_token

# ################################################################################################################################
