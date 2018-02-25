# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from uuid import uuid4

# regexp
import regex as re

# Zato
from zato.server.service import List, Service
from zato.server.service.internal.sso import BaseService, BaseSIO
from zato.sso import status_code, ValidationError
from zato.sso.odb.query import user_exists
from zato.sso.util import new_confirm_token

# ################################################################################################################################

class Signup(BaseService):
    """ Lets users sign up with the system.
    """
    class SimpleIO(BaseSIO):
        input_required = ('username', 'password', 'current_app', List('app_list'))
        input_optional = ('email', 'display_name', 'first_name', 'middle_name', 'last_name')
        output_optional = BaseSIO.output_optional + ('confirm_token',)

# ################################################################################################################################

    def _handle_sso(self, ctx):

        # Used to confirm that an account should be really opened
        confirm_token = new_confirm_token()

        # Always lower-cased so as to be treated in a uniform manner
        ctx.input.username = ctx.input.username.lower()
        ctx.input.email = ctx.input.get('email', '').lower()

        for name in ctx.sso_conf.user_validation.service:
            validation_response = self.invoke(name, {
                'username': ctx.input.username,
                'email': ctx.input.email,
                'password': ctx.input.password,
                'current_app': ctx.input.current_app,
                'app_list': ctx.input.app_list,
            }, as_bunch=True)

            if not validation_response.is_valid:
                # Substatus list is returned only if validation failed and it was confirmed that we are safe to return it
                # so we can just assign it to payload unconditionally.
                self.response.payload.status = validation_response.status
                self.response.payload.sub_status[:] = validation_response.sub_status

                # By default, this is always returned, no matter if successful or not, to prevent exploitation
                # by attackers trying to find out if a given user/email exists or not.
                if ctx.sso_conf.signup.always_return_confirm_token:
                    self.response.payload.confirm_token = confirm_token

                return

        # None of validation services returned an error so we can create the user now
        with closing(self.odb.session()) as session:
            user = self.sso.user.create_user(ctx.input)
            session.add(user)
            session.commit()

        # User is added, we can return the confirm token now and set an OK flag
        self.response.payload.status = status_code.ok
        self.response.payload.confirm_token = confirm_token

        # Invoke any callback services configured

# ################################################################################################################################

class Validate(Service):
    """ Validates creation of user data in accordance with configuration from sso.conf.
    """
    class SimpleIO:
        input_required = ('username', 'password', List('app_list'))
        input_optional = ('email',)
        output_required = ('is_valid',)
        output_optional = (List('status_code'), 'return_rc')
        encrypt_secrets = False
        response_elem = None

# ################################################################################################################################

    def _has_whitespace(self, data, _regexp=re.compile(r'\s', re.MULTILINE | re.UNICODE)):
        """ Returns True if data contains ASCII whitespace of any sort.
        """
        return _regexp.search(data)

# ################################################################################################################################

    def _validate_username_email(self, session, sso_conf, username, email, check_email):
        """ Validation common to usernames and emails.
        """
        # Check if user exists either by username or email
        user = user_exists(session, username, email, check_email)

        if user:

            if check_email:
                if user.username == username and user.email == email:
                    rc = [status_code.username.exists, status_code.email.exists]
                    return_rc = sso_conf.signup.inform_if_user_exists and sso_conf.signup.inform_if_email_exists

            elif user.username == username:
                rc = status_code.username.exists
                return_rc = sso_conf.signup.inform_if_user_exists

            elif user.email == email:
                rc = status_code.email.exists
                return_rc = sso_conf.signup.inform_if_email_exists

            raise ValidationError(rc, return_rc)

# ################################################################################################################################

    def _validate_username(self, session, sso_conf, username):
        """ Raises ValidationError if username is invalid, e.g. is not too long.
        """
        # Username must not be too long
        if len(username) > sso_conf.signup.max_length_username:
            raise ValidationError(status_code.username.too_long, sso_conf.signup.inform_if_user_invalid)

        # Username must not contain whitespace
        if self._has_whitespace(username):
            raise ValidationError(status_code.username.has_whitespace, sso_conf.signup.inform_if_user_invalid)

        # Username must not contain restricted keywords
        for elem in sso_conf.user_validation.reject_username:
            if elem in username:
                raise ValidationError(status_code.username.invalid, sso_conf.signup.inform_if_user_invalid)

# ################################################################################################################################

    def _validate_email(self, session, sso_conf, email):
        """ Raises ValidationError if email is invalid, e.g. already exists.
        """
        # E-mail may be required
        if sso_conf.signup.is_email_required and not email:
            raise ValidationError(status_code.email.missing, sso_conf.signup.inform_if_email_invalid)

        # E-mail must not be too long
        if len(email) > sso_conf.signup.max_length_email:
            raise ValidationError(status_code.email.too_long, sso_conf.signup.inform_if_email_invalid)

        # E-mail must not contain whitespace
        if self._has_whitespace(email):
            raise ValidationError(status_code.email.has_whitespace, sso_conf.signup.inform_if_email_invalid)

        # E-mail must not contain restricted keywords
        for elem in sso_conf.user_validation.reject_email:
            if elem in email:
                raise ValidationError(status_code.email.invalid, sso_conf.signup.inform_if_email_invalid)

# ################################################################################################################################

    def _validate_password(self, session, sso_conf, password):
        """ Raises ValidationError if password is invalid, e.g. it is too simple.
        """
        # Password may not be too short
        if len(password) < sso_conf.signup.min_length_password:
            raise ValidationError(status_code.password.too_short, sso_conf.signup.inform_if_password_invalid)

        # Password may not be too long
        if len(password) > sso_conf.signup.max_length_password:
            raise ValidationError(status_code.password.too_long, sso_conf.signup.inform_if_password_invalid)

        # Password's default complexity is checked case-insensitively
        password = password.lower()

        # Password may not contain most commonly used ones
        for elem in sso_conf.user_validation.reject_password:
            if elem in password:
                raise ValidationError(status_code.password.invalid, sso_conf.signup.inform_if_password_invalid)

# ################################################################################################################################

    def _validate_app_list(self, session, sso_conf, current_app, app_list):
        """ Raises ValidationError if input app_list is invalid, e.g. includes an unknown one.
        """
        # All of input apps must have been already defined in configuration
        for app in app_list:
            if app not in sso_conf.apps.all:
                raise ValidationError(status_code.app_list.invalid, sso_conf.signup.inform_if_app_invalid)

        # Current app, the one the user is signed up through, must allow user signup
        if current_app not in sso_conf.apps.signup_allowed:
            raise ValidationError(status_code.app_list.no_signup, sso_conf.signup.inform_if_app_invalid)

# ################################################################################################################################

    def handle(self, _invalid=uuid4().hex):

        # Local aliases
        sso_conf = self.server.sso_config
        input = self.request.input
        email = input.get('email') or _invalid # To make sure it never matches anything if not given on input

        # If e-mails are encrypted, we cannot look them up without decrypting them all,
        # which is not currently implemented.
        check_email = not sso_conf.main.encrypt_email

        with closing(self.odb.session()) as session:

            # Each of these calls may raise ValidationError, which we catch and return its subcode to our caller.
            try:

                # This one checks if username or email are not already taken using one SQL query
                self._validate_username_email(session, sso_conf, input.username, email, check_email)

                # These check individual elements
                self._validate_username(session, sso_conf, input.username)
                self._validate_password(session, sso_conf, input.password)
                if check_email:
                    self._validate_email(session, sso_conf, email)

            except ValidationError as e:
                self.response.payload.is_valid = False
                if e.return_rc:
                    self.response.payload.status_code = e.status_code
            else:
                self.response.payload.is_valid = True

# ################################################################################################################################
