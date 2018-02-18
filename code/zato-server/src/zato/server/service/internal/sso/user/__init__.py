# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from uuid import uuid4

# regex
import regex as re

# Zato
from zato.common.odb.query.sso import get_user_by_username, user_exists
from zato.common.sso import const, status_code, ValidationError
from zato.common.util.sso import validate_password
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

            raise ValidationError(sub_status, return_status, status)

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
                validate_password(sso_conf, input.password)
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

    def _check_credentials(self, ctx, user):
        password_decrypted = self.server.decrypt(user.password)
        return self.server.verify_hash(ctx.input.password, password_decrypted)

# ################################################################################################################################

    def _check_login_to_app_allowed(self, ctx):
        if ctx.input.current_app not in ctx.sso_conf.apps.login_allowed:
            if ctx.sso_conf.main.inform_if_app_invalid:
                self.response.payload.sub_status.append(status_code.app_list.invalid)
        else:
            return True

# ################################################################################################################################

    def _check_remote_ip_allowed(self, ctx, user, _invalid=object()):

        ip_allowed = ctx.sso_conf.login_list.get('my-admin', _invalid)

        # Shortcut in the simplest case
        if ip_allowed == '*':
            return True

        # Do not continue if user is not whitelisted but is required to
        if ip_allowed is _invalid:
            if ctx.sso_conf.login.reject_if_not_listed:
                return

        # User was found in configuration so now we need to check IPs allowed ..
        else:

            # .. but if there are no IPs configured for user, it means the person may not log in
            # regardless of reject_if_not_whitelisted, which is why it is checked separately.
            if not ip_allowed:
                return

            # There is at least one address or pattern to check again ..
            else:
                # .. but if no remote address was sent, we cannot continue.
                if not ctx.remote_addr:
                    return False
                else:
                    for _remote_addr in ctx.remote_addr:
                        for _ip_allowed in ip_allowed:
                            if _remote_addr in _ip_allowed:
                                return True # OK, there was at least that one match so we report success

                    # If we get here, it means that none of remote addresses from input matched
                    # so we can return False to be explicit.
                    return False

# ################################################################################################################################

    def _check_user_not_locked(self, ctx, user):
        if user.is_locked:
            if ctx.sso_conf.login.inform_if_locked:
                self.response.payload.sub_status.append(status_code.auth.locked)
        else:
            return True

# ################################################################################################################################

    def _check_signup_status(self, ctx, user):
        if user.sign_up_status != const.signup_status.final:
            if ctx.sso_conf.login.inform_if_not_confirmed:
                self.response.payload.sub_status.append(status_code.auth.invalid_signup_status)
        else:
            return True

# ################################################################################################################################

    def _check_is_approved(self, ctx, user):
        if not user.is_approved != const.signup_status.final:
            if ctx.sso_conf.login.inform_if_not_confirmed:
                self.response.payload.sub_status.append(status_code.auth.invalid_signup_status)
        else:
            return True

# ################################################################################################################################

    def _check_password_expired(self, ctx, user, _now=datetime.utcnow):
        if _now() > user.password_expiry:
            if ctx.sso_conf.password.inform_if_expired:
                self.response.payload.sub_status.append(status_code.password.expired)
        else:
            return True

# ################################################################################################################################

    def _check_password_about_to_expire(self, ctx, user, _now=datetime.utcnow, _timedelta=timedelta):

        # Find time after which the password is considered to be about to expire
        threshold_time = user.password_expiry - _timedelta(days=ctx.sso_conf.password.about_to_expire_threshold)

        # .. check if current time is already past that threshold ..
        if _now() > threshold_time:

            # .. if it is, we may either return a warning and continue ..
            if ctx.sso_conf.password.inform_if_about_to_expire:
                self.response.payload.status = status_code.warning
                self.response.payload.sub_status.append(status_code.password.w_about_to_exp)
                return status_code.warning

            # .. or it can considered an error, which rejects the request.
            else:
                self.response.payload.status = status_code.error
                self.response.payload.sub_status.append(status_code.password.e_about_to_exp)
                return status_code.error

        # No approaching expiry, we may continue
        else:
            return True

# ################################################################################################################################

    def _check_must_send_new_password(self, ctx, user):
        if user.password_must_change and not ctx.input.get('new_password'):
            if ctx.sso_conf.password.inform_if_must_be_changed:
                self.response.payload.sub_status.append(status_code.password.must_send_new)
        else:
            return True

# ################################################################################################################################

    def _handle_sso(self, ctx, _ok=status_code.ok):

        # Look up user and return if not found by username
        with closing(self.odb.session()) as session:
            user = get_user_by_username(session, ctx.input.username)
            if not user:
                return

        # Check credentials first to make sure that attackers do not learn about any sort
        # of metadata (e.g. is the account locked) if they do not know username and password.
        #if not self._check_credentials(ctx, user):
        #    return

        # It must be possible to log into the application requested (CRM above)
        if not self._check_login_to_app_allowed(ctx):
            return

        # If applicable, requests must originate in a white-listed IP address
        if not self._check_remote_ip_allowed(ctx, user):
            return

        # User must not have been locked out of the auth system
        if not self._check_user_not_locked(ctx, user):
            return

        # If applicable, user must be fully signed up, including account creation's confirmation
        if not self._check_signup_status(ctx, user):
            return

        # If applicable, user must be approved by a super-user
        if not self._check_is_approved(ctx, user):
            return

        # Password must not have expired
        if not self._check_password_expired(ctx, user):
            return

        # If applicable, password may not be about to expire (this must be after checking that it has not already).
        # Note that it may return a specific status to return (warning or error)
        _about_status = self._check_password_about_to_expire(ctx, user)
        if _about_status is not True:
            self.response.payload.status = _about_status
            return

        # If password is marked as as requiring a change upon next login but a new one was not sent, reject the request.
        if not self._check_must_send_new_password(ctx, user):
            return

        # If new password is required, we need to validate and save it before session can be created.
        # Note that at this point we already know that the old password was correct so it is safe to set the new one
        # if it is confirmed to be valid. Passwords are rarely changed to it is OK to open a new SQL session here
        # in addition to the one above instead of re-using it.
        try:
            validate_password(ctx.sso_conf, ctx.input.new_password)
        except ValidationError as e:
            if e.return_status:
                self.response.payload.status = e.status
                self.response.payload.sub_status = e.sub_status
        else:


        # All checks done, session is created, we can signal OK now
        self.response.payload.status = status_code.ok

# ################################################################################################################################
