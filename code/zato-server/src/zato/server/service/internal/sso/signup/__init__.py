# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.sso import new_confirm_token
from zato.server.service import List, Service

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from uuid import uuid4

# Zato
from zato.common.sso import reason_code
from zato.common.odb.query.sso import user_exists
from zato.common.util.sso import new_confirm_token
from zato.server.service import List, Service

# ################################################################################################################################

class ValidationError(Exception):
    """ Raised if any input SSO data is invalid, subcode contains details of what was rejected.
    """
    def __init__(self, reason_code, return_rc):
        self.reason_code = reason_code if isinstance(reason_code, list) else reason_code
        self.return_rc = return_rc

# ################################################################################################################################

class Validate(Service):
    """ Validates creation of user data in accordance with configuration from sso.conf.
    """
    class SimpleIO:
        input_required = ('username', 'password', List('app_list'))
        input_optional = ('email',)
        output_required = ('is_valid',)
        output_optional = (List('reason_code'), 'return_rc')
        encrypt_secrets = False
        response_elem = None

# ################################################################################################################################

    def _validate_username_email(self, session, sso_conf, username, email):
        """ Validation common to usernames and emails.
        """
        # Check if user exists either by username or email
        user = user_exists(session, username, email)

        if user:

            if user.username == username and user.email == email:
                rc = [reason_code.username.exists, reason_code.email.exists]
                return_rc = sso_conf.signup.inform_if_user_exists and sso_conf.signup.inform_if_email_exists

            elif user.username == username:
                rc = reason_code.username.exists
                return_rc = sso_conf.signup.inform_if_user_exists

            elif user.email == email:
                rc = reason_code.email.exists
                return_rc = sso_conf.signup.inform_if_email_exists

            raise ValidationError(rc, return_rc)

# ################################################################################################################################

    def _validate_username(self, session, sso_conf, username):
        """ Raises ValidationError if username is invalid, e.g. is not too long.
        """

# ################################################################################################################################

    def _validate_email(self, session, sso_conf, email):
        """ Raises ValidationError if email is invalid, e.g. already exists.
        """

    def _validate_password(self, session, sso_conf, password):
        """ Raises ValidationError if password is invalid, e.g. it is too simple.
        """

# ################################################################################################################################

    def _validate_app_list(self, session, sso_conf, app_list):
        """ Raises ValidationError if input app_list is invalid, e.g. includes an unknown one.
        """

# ################################################################################################################################

    def handle(self, _invalid=uuid4().hex):

        # Local aliases
        sso_conf = self.server.sso_config
        input = self.request.input
        email = input.get('email') or _invalid # To make it never matches anything if not given on input

        with closing(self.odb.session()) as session:

            # Each of these calls may raise ValidationError, which we catch and return its subcode to our caller.
            try:

                # This checks if username or email are not already taken using one SQL query
                self._validate_username_email(session, sso_conf, input.username, email)

                self._validate_username(session, sso_conf, input.username)
                self._validate_email(session, sso_conf, email)
                self._validate_password(session, sso_conf, input.password)

            except ValidationError as e:
                if e.return_rc:
                    self.response.payload.reason_code = e.reason_code

        self.response.payload.is_valid = True

# ################################################################################################################################

class SignUp(Service):
    """ Lets users sign up with the system.
    """
    class SimpleIO:
        input_required = ('username', 'password', List('app_list'))
        input_optional = ('email', 'display_name', 'first_name', 'middle_name', 'last_name')
        output_required = ('confirm_token',)
        output_optional = (List('reason_code'),)
        encrypt_secrets = False
        response_elem = None
        skip_empty_keys = True

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
        }, as_bunch=True)

        # Reason code list is returned only if validation failed and it was confirmed that we are safe to return it
        # so we can just assign it to payload unconditionally.
        self.response.payload.reason_code = validation_response.reason_code

        # This is always returned, no matter if input was valid or not
        self.response.payload.confirm_token = confirm_token

# ################################################################################################################################
'''
