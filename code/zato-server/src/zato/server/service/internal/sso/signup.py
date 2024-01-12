# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from uuid import uuid4

# regexp
import regex as re

# Zato
from zato.server.service import List, Service
from zato.sso import status_code, ValidationError
from zato.sso.odb.query import user_exists

# ################################################################################################################################

class Validate(Service):
    """ Validates creation of user data in accordance with configuration from sso.conf.
    """
    class SimpleIO:
        input_required = ('username', 'password', List('app_list'))
        input_optional = ('email',)
        output_required = ('is_valid',)
        output_optional = (List('sub_status'), 'return_status')
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
                    sub_status = [status_code.username.exists, status_code.email.exists]
                    return_status = sso_conf.signup.inform_if_user_exists and sso_conf.signup.inform_if_email_exists

            elif user.username == username:
                sub_status = status_code.username.exists
                return_status = sso_conf.signup.inform_if_user_exists

            elif user.email == email:
                sub_status = status_code.email.exists
                return_status = sso_conf.signup.inform_if_email_exists

            raise ValidationError(sub_status, return_status)

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
        # This may be encrypted while we need to validate its clear-text form
        password = self.server.decrypt(password)

        # Password may not be too short
        if len(password) < sso_conf.password.min_length:
            raise ValidationError(status_code.password.too_short, sso_conf.password.inform_if_invalid)

        # Password may not be too long
        if len(password) > sso_conf.password.max_length:
            raise ValidationError(status_code.password.too_long, sso_conf.password.inform_if_invalid)

        # Password's default complexity is checked case-insensitively
        password = password.lower()

        # Password may not contain most commonly used ones
        for elem in sso_conf.password.reject_list:
            if elem in password:
                raise ValidationError(status_code.password.invalid, sso_conf.password.inform_if_invalid)

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
                self.logger.warning('Could not validate user `%s`, sub_status `%s`', input.username, e.sub_status)
                self.response.payload.is_valid = False
                if e.return_status:
                    self.response.payload.sub_status = e.sub_status
            else:
                self.response.payload.is_valid = True

# ################################################################################################################################
