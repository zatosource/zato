# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta

# Zato
from zato.common.odb.model import SSOUser as UserModel
from zato.sso.odb.query import create_user

# ################################################################################################################################

class CreateUserCtx(object):
    """ A business object to carry user creation configuration around.
    """
    __slots__ = ('data', 'is_active', 'is_internal', 'is_approval_needed', 'is_super_user', 'password_expiry',
        'encrypt_password', 'encrypt_email', 'encrypt_func', 'hash_func', 'new_user_id_func', 'confirm_token')

    def __init__(self):
        self.data = None
        self.is_active = None
        self.is_internal = None
        self.is_approval_needed = None
        self.is_super_user = None
        self.password_expiry = None
        self.encrypt_password = None
        self.encrypt_email = None
        self.new_user_id_func = None
        self.confirm_token = None

# ################################################################################################################################

class UserAPI(object):
    """ The main object through SSO users are managed.
    """
    def __init__(self, odb, sso_conf, encrypt_func, hash_func, new_user_id_func):
        self.odb = odb
        self.sso_conf = sso_conf
        self.encrypt_func = encrypt_func
        self.hash_func = hash_func
        self.new_user_id_func = new_user_id_func
        self.encrypt_email = self.sso_conf.main.encrypt_email
        self.encrypt_password = self.sso_conf.main.encrypt_password
        self.password_expiry = self.sso_conf.password.expiry

# ################################################################################################################################

    def _create_user(session, data, is_active, is_internal, is_approval_needed, is_super_user, password_expiry, encrypt_password,
        encrypt_email, encrypt_func, hash_func, new_user_id_func, _utcnow=_utcnow, _timedelta=timedelta):

        # Always in UTC
        now = _utcnow()

        # Normalize input
        data.display_name = data.display_name.strip()
        data.first_name = data.first_name.strip()
        data.middle_name = data.middle_name.strip()
        data.last_name = data.last_name.strip()

        # If display_name is given on input, this will be the final value of that attribute ..
        if data.display_name:
            display_name = data.display_name.strip()

        # .. otherwise, display_name is a concatenation of first, middle and last name.
        else:
            display_name = ''

            if data.first_name:
                display_name += data.first_name
                display_name += ' '

            if data.middle_name:
                display_name += data.middle_name
                display_name += ' '

            if data.last_name:
                display_name += data.last_name

            display_name = display_name.strip()

        user_model = UserModel()
        user_model.user_id = new_user_id()
        user_model.is_active = is_active
        user_model.is_internal = is_internal
        user_model.is_approved = False if is_approval_needed else True
        user_model.is_locked = False
        user_model.is_super_user = is_super_user

        # Passwords are always at least hashed and possibly encrypted too ..
        password = make_password_secret(data.password, self.encrypt_password, encrypt_func, hash_func)

        # .. while emails are only encrypted, and it is optional.
        if self.encrypt_email:
            email = make_data_secret(data.email, encrypt_func)

        user_model.username = data.username
        user_model.email = email

        user_model.password = password
        user_model.password_is_set = True
        user_model.password_last_set = now
        user_model.password_must_change = False
        user_model.password_expiry = now + timedelta(days=self.password_expiry)

        user_model.sign_up_status = const.signup_status.before_confirmation
        user_model.sign_up_time = now

        user_model.display_name = display_name
        user_model.first_name = data.first_name
        user_model.middle_name = data.middle_name
        user_model.last_name = data.last_name

        # Uppercase any and all names for indexing purposes.
        user_model.display_name_upper = display_name.upper()
        user_model.first_name_upper = data.first_name.upper()
        user_model.middle_name_upper = data.middle_name.upper()
        user_model.last_name_upper = data.last_name.upper()

        return user_model

# ################################################################################################################################

    def create_super_user(self, ctx, new_user_id_func=None):
        """ Creates a new super-user out of initial user data.
        """
        ctx.is_active = True
        ctx.is_internal = False
        ctx.is_approval_needed = False
        ctx.is_super_user = True
        ctx.new_user_id_func = new_user_id_func or self.new_user_id_func
        ctx.confirm_token = None

        with closing(self.odb.session()) as session:
            user = self._create_user(ctx)
            session.add(user)
            session.commit()

# ################################################################################################################################

    def set_password(session, user_id, password, encrypt_password, encrypt_func, hash_func, must_change, password_expiry,
        _utcnow=_utcnow):
        """ Sets a new password of a user. The password must have been already validated.
        """
        session.execute(
            update(UserModelTable).\
            values({
                'password': make_password_secret(password, encrypt_password, encrypt_func, hash_func),
                'password_must_change': must_change,
                'password_is_set': True,
                'password_last_set': _utcnow(),
                'password_expiry': now + timedelta(days=password_expiry),
                }).\
            where(UserModelTable.c.user_id==user_id)
        )

# ################################################################################################################################
