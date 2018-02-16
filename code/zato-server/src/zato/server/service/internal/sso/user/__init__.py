# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from uuid import uuid4

# regex
import regex as re

# Zato
from zato.common.odb.query.sso import get_user_by_username, user_exists
from zato.common.sso import const, status_code, ValidationError
from zato.server.service import List, Service
from zato.server.service.internal.sso import BaseService, BaseSIO

# ################################################################################################################################

class Validate(Service):
    """ Validates creation of user data in accordance with configuration from sso.conf.
    """
    class SimpleIO(BaseSIO):
        input_required = ('username', 'password', List('app_list'))
        input_optional = ('email',)
        output_required = ('is_valid',)
        output_optional = BaseSIO.output_optional + ('return_status',)

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
                    status = status_code.error
                    sub_status = [status_code.username.exists, status_code.email.exists]
                    return_status = sso_conf.signup.inform_if_user_exists and sso_conf.signup.inform_if_email_exists

            elif user.username == username:
                status = status_code.error
                sub_status = status_code.username.exists
                return_status = sso_conf.signup.inform_if_user_exists

            elif user.email == email:
                status = status_code.error
                sub_status = status_code.email.exists
                return_status = sso_conf.signup.inform_if_email_exists

            raise ValidationError(status, sub_status, return_status)

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
                raise ValidationError(status_code.app_list.invalid, sso_conf.main.inform_if_app_invalid)

        # Current app, the one the user is signed up through, must allow user signup
        if current_app not in sso_conf.apps.signup_allowed:
            raise ValidationError(status_code.app_list.no_signup, sso_conf.main.inform_if_app_invalid)

# ################################################################################################################################

    def handle(self, _invalid=uuid4().hex):

        # Local aliases
        input = self.request.input
        sso_conf = self.server.sso_config
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
                if e.return_status:
                    self.response.payload.status = e.status
                    self.response.payload.sub_status = e.sub_status
            else:
                self.response.payload.is_valid = True

# ################################################################################################################################

class Login(BaseService):
    """ Logs a user in, provided that all authentication and authorization checks succeed.
    """
    class SimpleIO(BaseSIO):
        input_required = ('username', 'password', 'current_app')
        input_optional = ('new_password',)
        output_optional = BaseSIO.output_optional + ('ust',)

# ################################################################################################################################

    def _handle_sso(self, ctx):

        # Look up user and return if not found by username
        with closing(self.odb.session()) as session:
            user = get_user_by_username(session, ctx.input.username)
            if not user:
                return

        # Check credentials first to make sure that attackers do not learn about any sort
        # of metadata (e.g. is the account locked) if they do not know username and password.
        password_decrypted = self.server.decrypt(user.password)
        if not self.server.verify_hash(ctx.input.password, password_decrypted):
            return

        # It must be possible to log into the application requested (CRM above)
        if ctx.input.current_app not in ctx.sso_conf.apps.login_allowed:
            if ctx.sso_conf.main.inform_if_app_invalid:
                self.response.payload.sub_status.append(status_code.app_list.invalid)
            return

        # If applicable, requests must originate in a white-listed IP address

        # User must not have been locked out of the authentication system by a super-user
        if user.is_locked:
            if ctx.sso_conf.login.inform_if_locked:
                self.response.payload.sub_status.append(status_code.auth.locked)
            return

        # If applicable, user must be fully signed up, including account creation's confirmation
        if user.sign_up_status != const.signup_status.final:
            if ctx.sso_conf.login.inform_if_not_confirmed:
                self.response.payload.sub_status.append(status_code.auth.invalid_signup_status)
            return

        # If applicable, user must be approved by a super-user
        if not user.is_approved != const.signup_status.final:
            if ctx.sso_conf.login.inform_if_not_confirmed:
                self.response.payload.sub_status.append(status_code.auth.invalid_signup_status)
            return

        # If applicable, password may not be about to expire
        # Password must not have expired
        # Password must not be marked as requiring a change upon next login

        # All checks done, session is created, we can signal OK now
        self.response.payload.status = status_code.ok

# ################################################################################################################################
