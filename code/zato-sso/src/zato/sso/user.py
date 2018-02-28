# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from copy import deepcopy
from datetime import datetime, timedelta
from json import dumps
from logging import getLogger
from traceback import format_exc

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.crypto import CryptoManager
from zato.common.odb.model import SSOUser as UserModel
from zato.sso import const, status_code, ValidationError
from zato.sso.odb.query import get_user_by_id, get_user_by_username, get_user_by_ust, is_super_user_by_ust
from zato.sso.session import LoginCtx, SessionAPI
from zato.sso.util import make_data_secret, make_password_secret, set_password, validate_password

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

_utcnow = datetime.utcnow
_gen_secret = CryptoManager.generate_secret
UserModelTable = UserModel.__table__

# ################################################################################################################################

# Attributes accessible to both account owner and super-users
regular_attrs = {
    'user_id': None,
    'username': None,
    'email': b'',
    'display_name': '',
    'first_name': '',
    'middle_name': '',
    'last_name': '',
}

# Attributes accessible only to super-users
super_user_attrs = {
    'is_active': False,
    'is_internal': False,
    'is_super_user': False,
    'is_approved': False,
    'is_locked': True,
    'locked_time': None,
    'creation_ctx': '',
    'locked_by': None,
    'approv_rej_time': None,
    'approv_rej_by': None,
    'password_expiry': 0,
    'password_is_set': False,
    'password_must_change': True,
    'password_last_set': None,
    'sign_up_status': None,
    'sign_up_time': None,
}

# This can be only changed but never read
_write_only = {
    'password': None,
}

_all_super_user_attrs = {}
_all_super_user_attrs.update(regular_attrs)
_all_super_user_attrs.update(super_user_attrs)

_all_attrs = deepcopy(_all_super_user_attrs)
_all_attrs.update(_write_only)

# ################################################################################################################################

class Forbidden(Exception):
    def __init__(self, message='You are not authorized to access this resource'):
        super(Forbidden, self).__init__(message)

# ################################################################################################################################

class User(object):
    """ A user entity representing a person in SSO.
    """
    __slots__ = _all_attrs.keys()

    def __init__(self, **kwargs):
        for kwarg_name, kwarg_value in kwargs.items():
            setattr(self, kwarg_name, kwarg_value)

        for attr_name, attr_value in _all_attrs.items():
            if attr_name not in kwargs:
                setattr(self, attr_name, attr_value)

# ################################################################################################################################

class CreateUserCtx(object):
    """ A business object to carry user creation configuration around.
    """
    __slots__ = ('data', 'is_active', 'is_internal', 'is_approval_needed', 'is_approved', 'is_super_user', 'password_expiry',
        'encrypt_password', 'encrypt_email', 'encrypt_func', 'hash_func', 'new_user_id_func', 'confirm_token',
        'sign_up_status')

    def __init__(self, data=None):
        self.data = data
        self.is_active = None
        self.is_internal = None
        self.is_approval_needed = None
        self.is_approved = None
        self.is_super_user = None
        self.password_expiry = None
        self.encrypt_password = None
        self.encrypt_email = None
        self.new_user_id_func = None
        self.confirm_token = None
        self.sign_up_status = None

# ################################################################################################################################

class UserAPI(object):
    """ The main object through SSO users are managed.
    """
    def __init__(self, sso_conf, odb_session_func, encrypt_func, decrypt_func, hash_func, verify_hash_func, new_user_id_func):
        self.sso_conf = sso_conf
        self.odb_session_func = odb_session_func
        self.encrypt_func = encrypt_func
        self.decrypt_func = decrypt_func
        self.hash_func = hash_func
        self.verify_hash_func = verify_hash_func
        self.new_user_id_func = new_user_id_func
        self.encrypt_email = self.sso_conf.main.encrypt_email
        self.encrypt_password = self.sso_conf.main.encrypt_password
        self.password_expiry = self.sso_conf.password.expiry

        # For convenience, sessions are accessible through user API.
        self.session = SessionAPI(self.sso_conf, self.encrypt_func, self.decrypt_func, self.hash_func, self.verify_hash_func)

# ################################################################################################################################

    def set_odb_session_func(self, func):
        self.odb_session_func = func
        self.session.set_odb_session_func(func)

# ################################################################################################################################

    def _create_sql_user(self, ctx, _utcnow=_utcnow, _timedelta=timedelta):

        # Always in UTC
        now = _utcnow()

        # Normalize input
        ctx.data['display_name'] = ctx.data.get('display_name', '').strip()
        ctx.data['first_name'] = ctx.data.get('first_name', '').strip()
        ctx.data['middle_name'] = ctx.data.get('middle_name', '').strip()
        ctx.data['last_name'] = ctx.data.get('last_name', '').strip()

        # If display_name is given on input, this will be the final value of that attribute ..
        if ctx.data['display_name']:
            display_name = ctx.data['display_name'].strip()

        # .. otherwise, display_name is a concatenation of first, middle and last name.
        else:
            display_name = ''

            if ctx.data['first_name']:
                display_name += ctx.data['first_name']
                display_name += ' '

            if ctx.data['middle_name']:
                display_name += ctx.data['middle_name']
                display_name += ' '

            if ctx.data['last_name']:
                display_name += ctx.data['last_name']

            display_name = display_name.strip()

        user_model = UserModel()
        user_model.user_id = ctx.data.get('user_id') or self.new_user_id_func()
        user_model.is_active = ctx.is_active
        user_model.is_internal = ctx.is_internal
        user_model.is_approved = False if ctx.is_approval_needed else True
        user_model.is_locked = ctx.data.get('is_locked') or False
        user_model.is_super_user = ctx.is_super_user
        user_model.creation_ctx = dumps(ctx.data.get('creation_ctx'))

        # Generate a strong password if one is not given on input ..
        if not ctx.data.get('password'):
            ctx.data['password'] = CryptoManager.generate_password()

        # .. and if it is, make sure it gets past validation.
        else:
            self.validate_password(ctx.data['password'])

        # Passwords must be strong and are always at least hashed and possibly encrypted too ..
        password = make_password_secret(
            ctx.data['password'].encode('utf8'), self.encrypt_password, self.encrypt_func, self.hash_func)

        # .. while emails are only encrypted, and it is optional.
        if self.encrypt_email:
            email = make_data_secret(ctx.data.get('email').encode('utf8') or b'', self.encrypt_func)

        user_model.username = ctx.data['username']
        user_model.email = email

        user_model.password = password
        user_model.password_is_set = True
        user_model.password_last_set = now
        user_model.password_must_change = ctx.data.get('password_must_change') or False
        user_model.password_expiry = now + timedelta(days=self.password_expiry)

        user_model.sign_up_status = ctx.data.get('sign_up_status')
        user_model.sign_up_time = now
        user_model.sign_up_confirm_token = _gen_secret(192)

        user_model.display_name = display_name
        user_model.first_name = ctx.data['first_name']
        user_model.middle_name = ctx.data['middle_name']
        user_model.last_name = ctx.data['last_name']

        # Uppercase any and all names for indexing purposes.
        user_model.display_name_upper = display_name.upper()
        user_model.first_name_upper = ctx.data['first_name'].upper()
        user_model.middle_name_upper = ctx.data['middle_name'].upper()
        user_model.last_name_upper = ctx.data['last_name'].upper()

        return user_model

# ################################################################################################################################

    def _require_super_user(self, ust, current_app, remote_addr):
        """ Raises an exception if either current user session token does not belong to a super user.
        """
        self._get_current_session(ust, current_app, remote_addr, needs_super_user=True)

# ################################################################################################################################

    def _create_user(self, ctx, is_super_user, ust=None, current_app=None, remote_addr=None, skip_sec=None):
        """ Creates a new regular or super-user out of initial user data.
        """
        with closing(self.odb_session_func()) as session:

            if not skip_sec:
                self._require_super_user(ust, current_app, remote_addr)

            # The only field always required
            if not ctx.data.get('username'):
                logger.warn('Missing `username` on input')
                raise ValidationError(status_code.username.invalid, True)

            # Make sure the username is unique
            if get_user_by_username(session, ctx.data['username']):
                logger.warn('Username `%s` already exists', ctx.data['username'])
                raise ValidationError(status_code.username.exists, False)

            ctx.is_active = True
            ctx.is_internal = False
            ctx.is_approval_needed = False
            ctx.is_approved = True
            ctx.is_super_user = is_super_user
            ctx.confirm_token = None

            if not ctx.data.get('sign_up_status', None):
                ctx.data['sign_up_status'] = const.signup_status.final

            user = self._create_sql_user(ctx)

            # Note that externally visible .id is .user_id on SQL level,
            # this is on purpose because internally SQL .id is used only for joins.
            ctx.data['user_id'] = user.user_id
            ctx.data['display_name'] = user.display_name
            ctx.data['first_name'] = user.first_name
            ctx.data['middle_name'] = user.middle_name
            ctx.data['last_name'] = user.last_name
            ctx.data['is_active'] = user.is_active
            ctx.data['is_internal'] = user.is_internal
            ctx.data['is_approved'] = user.is_approved
            ctx.data['is_locked'] = user.is_locked
            ctx.data['is_super_user'] = user.is_super_user
            ctx.data['password_is_set'] = user.password_is_set
            ctx.data['password_last_set'] = user.password_last_set
            ctx.data['password_must_change'] = user.password_must_change
            ctx.data['password_expiry'] = user.password_expiry
            ctx.data['sign_up_status'] = user.sign_up_status
            ctx.data['sign_up_time'] = user.sign_up_time

            # This one we do not want to reveal back
            ctx.data.pop('password', None)

            session.add(user)
            session.commit()

# ################################################################################################################################

    def create_user(self, data, ust=None, current_app=None, remote_addr=None, skip_sec=False):
        """ Creates a new regular user.
        """
        return self._create_user(CreateUserCtx(data), False, ust, current_app, remote_addr, skip_sec)

# ################################################################################################################################

    def create_super_user(self, data, ust=None, current_app=None, remote_addr=None, skip_sec=False):
        """ Creates a new super-user.
        """
        # Super-users don't need to confirmation their own creation
        data['sign_up_status'] = const.signup_status.final

        return self._create_user(CreateUserCtx(data), True, ust, current_app, remote_addr, skip_sec)

# ################################################################################################################################

    def set_password(self, user_id, password, must_change, password_expiry, _utcnow=_utcnow):
        """ Sets a new password for user.
        """
        set_password(self.odb_session_func, self.encrypt_func, self.hash_func, self.sso_conf, user_id, password,
            must_change, password_expiry)

# ################################################################################################################################

    def get_user_by_username(self, username):
        """ Returns a user object by username or None, if there is no such username.
        """
        with closing(self.odb_session_func()) as session:
            return get_user_by_username(session, username)

# ################################################################################################################################

    def _get_current_session(self, current_ust, current_app, remote_addr, needs_super_user):
        """ Returns current session info or raises an exception if it could not be found.
        Optionally, requires that a super-user be owner of current_ust.
        """
        # Verify current session's very existence first ..
        current_session = self.session.get(current_ust, current_app, remote_addr)
        if not current_session:
            logger.warn('Could not verify session `%s` `%s` `%s` `%s`',
                current_ust, current_app, remote_addr, format_exc())
            raise ValidationError(status_code.auth.not_allowed, True)

        # .. the session exists but it may be still the case that we require a super-user on input.
        if needs_super_user:
            if not current_session.is_super_user:
                logger.warn(
                    'Current UST does not belong to a super-user, cannot continue, current user is `%s` `%s`',
                    current_session.user_id, current_session.username)
                raise ValidationError(status_code.auth.not_allowed, True)

# ################################################################################################################################

    def _get_user_by_attr(self, func, attr_value, current_ust, current_app, remote_addr, _needs_super_user,
        queries_current_session, _utcnow=_utcnow):
        """ Returns a user by a specific function and business value.
        """
        with closing(self.odb_session_func()) as session:

            # Validate and get session
            current_session = self._get_current_session(current_ust, current_app, remote_addr, _needs_super_user)

            # If func was to query current session, we can just re-use what we have fetched above,
            # so as to have one SQL query less in a piece of code that will be likely used very often.
            if queries_current_session:
                info = current_session
            else:
                info = func(session, attr_value, _utcnow())

            # Input UST is invalid for any reason (perhaps has just expired), raise an exception in that case
            if not info:
                raise ValidationError(status_code.auth.not_allowed, True)

            # UST is valid, let's return data then ..
            else:

                # .. but they into account if current user is a super-user or a regular one.
                out = {}
                attrs = _all_super_user_attrs if current_session.is_super_user else regular_attrs

                for key in attrs:
                    value = getattr(info, key)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    out[key] = value

                if out.get('email'):
                    if self.sso_conf.main.encrypt_email:
                        try:
                            out['email'] = self.decrypt_func(out['email'])
                        except Exception:
                            logger.warn('Could not decrypt email, user_id:`%s`', out['user_id'])

                return out

# ################################################################################################################################

    def get_user_by_ust(self, current_ust, current_app, remote_addr):
        """ Returns a user object by that person's current UST.
        """
        return self._get_user_by_attr(
            get_user_by_ust, self.decrypt_func(current_ust), current_ust, current_app, remote_addr, False, True)

# ################################################################################################################################

    def get_user_by_id(self, user_id, current_ust, current_app, remote_addr):
        """ Returns a user object by that person's ID.
        """
        return self._get_user_by_attr(get_user_by_id, user_id, current_ust, current_app, remote_addr, True, False)

# ################################################################################################################################

    def validate_password(self, password):
        return validate_password(self.sso_conf, password)

# ################################################################################################################################

    def delete_user(self, user_id=None, username=None):
        if not(user_id or username):
            raise ValueError('Exactly one of user_id and username is required')
        else:
            if user_id and username:
                raise ValueError('Cannot provide both user_id and username on input')

        if user_id:
            where = UserModelTable.c.user_id==user_id
        elif username:
            where = UserModelTable.c.username==username

        with closing(self.odb_session_func()) as session:
            session.execute(
                UserModelTable.delete().\
                where(where)
            )
            session.commit()

# ################################################################################################################################

    def _lock_user(self, user_id, is_locked):
        """ Locks or unlocks a user account.
        """
        with closing(self.odb_session_func()) as session:
            session.execute(
                update(UserModelTable).\
                values({
                    'is_locked': is_locked,
                    }).\
                where(UserModelTable.c.user_id==user_id)
            )
            session.commit()

# ################################################################################################################################

    def lock_user(self, user_id):
        """ Locks a user account.
        """
        self._lock_user(user_id, True)

# ################################################################################################################################

    def unlock_user(self, user_id):
        """ Unlocks a user account.
        """
        self._lock_user(user_id, False)

# ################################################################################################################################

    def login(self, username, password, current_app, remote_addr, user_agent, has_remote_addr=False,
        has_user_agent=False, new_password=''):
        """ Logs a user in if username and password are correct, returning a user session token (UST) on success,
        or a ValidationError on error.
        """
        return self.session.login(
            LoginCtx(
                remote_addr,
                user_agent,
                has_remote_addr,
                has_user_agent,
                {
                    'username': username,
                    'password': password,
                    'current_app': current_app,
                    'new_password': new_password
            }))

# ################################################################################################################################

    def logout(self, ust, current_app, remote_addr):
        """ Logs a user out of SSO.
        """
        return self.session.logout(ust, current_app, remote_addr)

# ################################################################################################################################
