'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from uuid import uuid4

# regex
import regex as re

# Zato
from zato.common.sso import const, reason_code
from zato.common.odb.model import SSOUser as UserModel
from zato.common.odb.query.sso import user_exists
from zato.common.util.sso import new_confirm_token, new_user_id
from zato.server.service import List, Service

# ################################################################################################################################

_utcnow = datetime.utcnow

# ################################################################################################################################

class User(object):
    """ An SSO user and related attributes.
    """
    def __init__(self):
        self.user_id = None
        self.is_active = None
        self.is_internal = None
        self.is_locked = None
        self.locked_time = None
        self.locked_by = None
        self.username = None
        self.password = None
        self.password_is_set = None
        self.password_must_change = None
        self.password_expiry = None
        self.sign_up_status = None
        self.sign_up_time = None
        self.sign_up_confirm_time = None
        self.email = None
        self.display_name = None
        self.first_name = None
        self.middle_name = None
        self.last_name = None
        self.display_name_upper = None
        self.first_name_upper = None
        self.middle_name_upper = None
        self.last_name_upper = None

    @staticmethod
    def signup(session, input, is_approval_needed, password_expiry, encrypt_password, encrypt_email, encrypt_func,
        hash_func, _utcnow=_utcnow, _timedelta=timedelta):

        # Always in UTC
        now = _utcnow()

        # Normalize input
        input.display_name = input.display_name.strip()
        input.first_name = input.first_name.strip()
        input.middle_name = input.middle_name.strip()
        input.last_name = input.last_name.strip()

        # If display_name is given on input, this will be the final value of that attribute ..
        if input.display_name:
            display_name = input.display_name.strip()

        # .. otherwise, display_name is a concatenation of first, middle and last name.
        else:
            display_name = ''

            if input.first_name:
                display_name += input.first_name
                display_name += ' '

            if input.middle_name:
                display_name += input.middle_name
                display_name += ' '

            if input.last_name:
                display_name += input.last_name

            display_name = display_name.strip()

        user_model = UserModel()
        user_model.user_id = new_user_id()
        user_model.is_active = True
        user_model.is_internal = True
        user_model.is_approved = False if is_approval_needed else True
        user_model.is_locked = False
        user_model.is_super_user = False

        # E.g. PBKDF2-SHA512
        password = hash_func(input.password)

        # Fernet (AES-128)
        if encrypt_password:
            password = encrypt_func(password)

        # Again, Fernet key
        email = encrypt_func(input.email) if encrypt_email else input.email

        user_model.username = input.username
        user_model.email = email
        user_model.password = password
        user_model.password_is_set = True
        user_model.password_must_change = False
        user_model.password_expiry = now + timedelta(days=password_expiry)

        user_model.sign_up_status = const.signup_status.before_confirmation
        user_model.sign_up_time = now

        user_model.display_name = display_name
        user_model.first_name = input.first_name
        user_model.middle_name = input.middle_name
        user_model.last_name = input.last_name

        # Uppercase any and all names for indexing purposes.
        user_model.display_name_upper = display_name.upper()
        user_model.first_name_upper = input.first_name.upper()
        user_model.middle_name_upper = input.middle_name.upper()
        user_model.last_name_upper = input.last_name.upper()

        return user_model

# ################################################################################################################################

class ValidationError(Exception):
    """ Raised if any input SSO data is invalid, subcode contains details of what was rejected.
    """
    def __init__(self, reason_code, return_rc):
        self.reason_code = reason_code if isinstance(reason_code, list) else [reason_code]
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
        # Username must not be too long
        if len(username) > sso_conf.signup.max_length_username:
            raise ValidationError(reason_code.username.too_long, sso_conf.signup.inform_if_user_invalid)

        # Username must not contain whitespace
        if self._has_whitespace(username):
            raise ValidationError(reason_code.username.has_whitespace, sso_conf.signup.inform_if_user_invalid)

        # Username must not contain restricted keywords
        for elem in sso_conf.user_validation.reject_username:
            if elem in username:
                raise ValidationError(reason_code.username.invalid, sso_conf.signup.inform_if_user_invalid)

# ################################################################################################################################

    def _validate_email(self, session, sso_conf, email):
        """ Raises ValidationError if email is invalid, e.g. already exists.
        """
        # E-mail may be required
        if sso_conf.signup.is_email_required and not email:
            raise ValidationError(reason_code.email.missing, sso_conf.signup.inform_if_email_invalid)

        # E-mail must not be too long
        if len(email) > sso_conf.signup.max_length_email:
            raise ValidationError(reason_code.email.too_long, sso_conf.signup.inform_if_email_invalid)

        # E-mail must not contain whitespace
        if self._has_whitespace(email):
            raise ValidationError(reason_code.email.has_whitespace, sso_conf.signup.inform_if_email_invalid)

        # E-mail must not contain restricted keywords
        for elem in sso_conf.user_validation.reject_email:
            if elem in email:
                raise ValidationError(reason_code.email.invalid, sso_conf.signup.inform_if_email_invalid)

# ################################################################################################################################

    def _validate_password(self, session, sso_conf, password):
        """ Raises ValidationError if password is invalid, e.g. it is too simple.
        """
        # Password may not be too short
        if len(password) < sso_conf.signup.min_length_password:
            raise ValidationError(reason_code.password.too_short, sso_conf.signup.inform_if_password_invalid)

        # Password may not be too long
        if len(password) > sso_conf.signup.max_length_password:
            raise ValidationError(reason_code.password.too_long, sso_conf.signup.inform_if_password_invalid)

        # Password's default complexity is checked case-insensitively
        password = password.lower()

        # Password may not contain most commonly used ones
        for elem in sso_conf.user_validation.reject_password:
            if elem in password:
                raise ValidationError(reason_code.password.invalid, sso_conf.signup.inform_if_password_invalid)

# ################################################################################################################################

    def _validate_app_list(self, session, sso_conf, current_app, app_list):
        """ Raises ValidationError if input app_list is invalid, e.g. includes an unknown one.
        """
        # All of input apps must have been already defined in configuration
        for app in app_list:
            if app not in sso_conf.apps.all:
                raise ValidationError(reason_code.app_list.invalid, sso_conf.signup.inform_if_app_invalid)

        # Current app, the one the user is signed up through, must allow user signup
        if current_app not in sso_conf.apps.signup_allowed:
            raise ValidationError(reason_code.app_list.no_signup, sso_conf.signup.inform_if_app_invalid)

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
                    self.response.payload.reason_code = e.reason_code
            else:
                self.response.payload.is_valid = True

# ################################################################################################################################

class SignUp(Service):
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

        validation_response = self.invoke(Validate.get_name(), {
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

        # Input was valid so we can create the user now
        with closing(self.odb.session()) as session:
            user = User.signup(session, input, sso_conf.signup.is_approval_needed, sso_conf.signup.password_expiry,
                sso_conf.main.encrypt_password, sso_conf.main.encrypt_email, self.server.encrypt, self.server.hash_secret)
            session.add(user)
            session.commit()

        # Invoke any callback services configured

# ################################################################################################################################
'''
