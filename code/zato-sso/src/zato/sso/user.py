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
from sqlalchemy import update as sql_update

# Zato
from zato.common.crypto import CryptoManager
from zato.common.odb.model import SSOUser as UserModel
from zato.sso import const, status_code, ValidationError
from zato.sso.odb.query import get_user_by_id, get_user_by_username, get_user_by_ust
from zato.sso.session import LoginCtx, SessionAPI
from zato.sso.util import check_credentials, make_data_secret, make_password_secret, set_password, validate_password

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
    'is_locked': True,
    'locked_time': None,
    'creation_ctx': '',
    'locked_by': None,
    'approval_status': None,
    'approval_status_mod_by': None,
    'approval_status_mod_time': None,
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

_no_such_value = object()

# ################################################################################################################################

class update:

    # Accessible to regular users only
    regular_attrs = set(('email', 'display_name', 'first_name', 'middle_name', 'last_name'))

    # Accessible to super-users only
    super_user_attrs = set(('is_approved', 'is_locked', 'password_expiry', 'password_must_change', 'sign_up_status',
        'approval_status'))

    # All updateable attributes
    all_update_attrs = regular_attrs.union(super_user_attrs)

    # All updateable attributes + user_id
    all_attrs = all_update_attrs.union(set(['user_id']))

    # There cannot be more than this many attributes on input
    max_len_attrs = len(all_update_attrs)

    # All boolean attributes
    boolean_attrs = ('is_approved', 'is_locked', 'password_must_change')

    # All datetime attributes
    datetime_attrs = ('password_expiry',)

    # All attributes that may be set to None / NULL
    none_allowed = set(regular_attrs)

# ################################################################################################################################

class change_password:

    # Accessible to regular users only
    regular_attrs = set(('old_password', 'new_password'))

    # Accessible to super-users only
    super_user_attrs = set(('new_password', 'password_expiry', 'password_must_change'))

    # This is used only for input validation which is why it is not called 'all_update_attrs'
    all_attrs = regular_attrs.union(super_user_attrs).union(set(['user_id']))

    # There cannot be more than this many attributes on input
    max_len_attrs = len(all_attrs)

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
    __slots__ = ('data', 'is_active', 'is_internal', 'is_super_user', 'password_expiry', 'encrypt_password', 'encrypt_email',
        'encrypt_func', 'hash_func', 'new_user_id_func', 'confirm_token', 'sign_up_status')

    def __init__(self, data=None):
        self.data = data
        self.is_active = None
        self.is_internal = None
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
            email = make_data_secret(ctx.data.get('email', '').encode('utf8') or b'', self.encrypt_func)

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

        user_model.sign_up_status = ctx.data.get('sign_up_status')
        user_model.sign_up_time = now
        user_model.sign_up_confirm_token = _gen_secret(192)

        user_model.approval_status = ctx.data['approval_status']
        user_model.approval_status_mod_time = now
        user_model.approval_status_mod_by = ctx.data['approval_status_mod_by']

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
        return self._get_current_session(ust, current_app, remote_addr, needs_super_user=True)

# ################################################################################################################################

    def _create_user(self, ctx, is_super_user, ust=None, current_app=None, remote_addr=None, skip_sec=None):
        """ Creates a new regular or super-user out of initial user data.
        """
        with closing(self.odb_session_func()) as session:

            if not skip_sec:
                current_session = self._require_super_user(ust, current_app, remote_addr)
                ctx.data['approval_status_mod_by'] = current_session.user_id
                if self.sso_conf.signup.is_approval_needed:
                    approval_status = const.approval_status.before_decision
                else:
                    approval_status = const.approval_status.approved

                ctx.data['approval_status'] = approval_status

            else:
                ctx.data['approval_status_mod_by'] = 'auto'
                ctx.data['approval_status'] = const.approval_status.approved

            # The only field always required
            if not ctx.data.get('username'):
                logger.warn('Missing `username` on input')
                raise ValidationError(status_code.username.invalid, True)

            # Make sure the username is unique
            if get_user_by_username(session, ctx.data['username'], needs_approved=False):
                logger.warn('Username `%s` already exists', ctx.data['username'])
                raise ValidationError(status_code.username.exists, False)

            ctx.is_active = True
            ctx.is_internal = False
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
            ctx.data['approval_status'] = user.approval_status
            ctx.data['approval_status_mod_time'] = user.approval_status_mod_time
            ctx.data['approval_status_mod_by'] = user.approval_status_mod_by
            ctx.data['is_approval_needed'] = self.sso_conf.signup.is_approval_needed
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

    def get_user_by_username(self, username, needs_approved=True):
        """ Returns a user object by username or None, if there is no such username.
        """
        with closing(self.odb_session_func()) as session:
            return get_user_by_username(session, username, needs_approved=needs_approved)

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

        return current_session

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
                if current_session.is_super_user:
                    attrs = _all_super_user_attrs
                    out = {
                        'is_approval_needed': self.sso_conf.signup.is_approval_needed
                    }
                else:
                    attrs = regular_attrs
                    out = {}


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

    def get_current_user(self, current_ust, current_app, remote_addr):
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

    def _delete_user(self, user_id, username, current_ust, current_app, remote_addr, skip_sec=False):
        """ Deletes a user by ID or username.
        """
        current_session = self._get_current_session(current_ust, current_app, remote_addr, needs_super_user=False)
        if not skip_sec:
            if not current_session.is_super_user:
                raise ValidationError(status_code.auth.not_allowed, False)

        if not(user_id or username):
            raise ValueError('Exactly one of user_id and username is required')
        else:
            if user_id and username:
                raise ValueError('Cannot provide both user_id and username on input')

        with closing(self.odb_session_func()) as session:

            # Make sure user_id actually exists ..
            if user_id:
                user = get_user_by_id(session, user_id)
                where = UserModelTable.c.user_id==user_id

            # .. or use username if this is what was given on input.
            elif username:
                user = get_user_by_username(session, username, needs_approved=False)
                where = UserModelTable.c.username==username

            # Make sure the user exists at all
            if not user:
                raise ValidationError(status_code.common.invalid_operation, False)

            # Users cannot delete themselves
            if user.user_id == current_session.user_id:
                raise ValidationError(status_code.common.invalid_operation, False)

            rows_matched = session.execute(
                UserModelTable.delete().\
                where(where)
            ).rowcount
            session.commit()

            if rows_matched != 1:
                msg = 'Expected for rows_matched to be 1 instead of %d, user_id:`%s`, username:`%s`'
                logger.warn(msg, rows_matched, user_id, username)

# ################################################################################################################################

    def delete_user_by_id(self, user_id, current_ust, current_app, remote_addr, skip_sec=False):
        """ Deletes a user by that person's ID.
        """
        return self._delete_user(user_id, None, current_ust, current_app, remote_addr, skip_sec)

# ################################################################################################################################

    def delete_user_by_username(self, username, current_ust, current_app, remote_addr, skip_sec=False):
        """ Deletes a user by that person's username.
        """
        return self._delete_user(None, username, current_ust, current_app, remote_addr, skip_sec)

# ################################################################################################################################

    def _lock_user_cli(self, user_id, is_locked):
        """ Locks or unlocks a user account. Used by CLI, does not check any permissions.
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

    def lock_user_cli(self, user_id):
        """ Locks a user account. Does not check any permissions.
        """
        self._lock_user(user_id, True)

# ################################################################################################################################

    def unlock_user_cli(self, user_id):
        """ Unlocks a user account. Does not check any permissions.
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

    def _ensure_no_unknown_update_attrs(self, attrs_allowed, data):
        """ Makes sure that update data contains only attributes explicitly allowed.
        """
        unexpected = []
        for attr in data:
            if attr not in attrs_allowed:
                unexpected.append(attr)

        if unexpected:
            logger.warn('Unexpected data on input %s', unexpected)
            raise ValidationError(status_code.common.invalid_input, False)

# ################################################################################################################################

    def _check_basic_update_attrs(self, data, max_len_attrs, all_update_attrs):
        """ Checks basic validity of user attributes that are about to be changed.
        """
        # Double-check we have data to update a user with ..
        if not data:
            raise ValidationError(status_code.common.missing_input, False)
        else:
            # .. and that no one attempts to overload us with it ..
            if len(data) > max_len_attrs:
                logger.warn('Too many data arguments %d > %d', len(data), max_len_attrs)
                raise ValidationError(status_code.common.invalid_input, False)

            # .. also, make sure that, no matter what kind of user this is, only supported arguments are given on input.
            # Later on we will fine-check it again to take the user's role into account, but we want to want to check it here
            # first on a rough level so as to avoid an SQL query in case of an error at this early stage.
            else:
                self._ensure_no_unknown_update_attrs(all_update_attrs, data)

# ################################################################################################################################

    def _update_user(self, data, current_ust, current_app, remote_addr, user_id=None, update_self=None):
        """ Low-level implementation of user updates.
        """
        if not(user_id or update_self):
            logger.warn('At least one of user_id or update_self is required')
            raise ValidationError(status_code.common.invalid_input, False)

        # Basic checks first
        self._check_basic_update_attrs(data, update.max_len_attrs, update.all_update_attrs)

        with closing(self.odb_session_func()) as session:
            current_session = self._get_current_session(current_ust, current_app, remote_addr, needs_super_user=False)

            # We will be updating our own account or another user, depending on input flags/parameters.
            _user_id = current_session.user_id if update_self else user_id

            # Super-users may update the whole set of attributes in existence.
            if current_session.is_super_user:
                attrs_allowed = update.all_update_attrs
            else:

                # If current session belongs to a regular user yet a user_id was given on input,
                # we may not continue because only super-users may update other users.
                if user_id and user_id != current_session.user_id:
                    logger.warn('Current user `%s` is not a super-user, cannot update user `%s`',
                        current_session.user_id, user_id)
                    raise ValidationError(status_code.common.invalid_input, False)

                # whereas regular users may change only basic attributes.
                attrs_allowed = update.regular_attrs

            # Make sure current user provided only these attributes that have been explicitly allowed
            self._ensure_no_unknown_update_attrs(attrs_allowed, data)

            # If sign_up_status was given on input, it must be among allowed values
            sign_up_status = data.get('sign_up_status')
            if sign_up_status and sign_up_status not in const.signup_status():
                logger.warn('Invalid sign_up_status `%s`', sign_up_status)
                raise ValidationError(status_code.common.invalid_input, False)

            # All booleans must be actually booleans
            for attr in update.boolean_attrs:
                value = data.get(attr, _no_such_value)
                if value is not _no_such_value:
                    if not isinstance(value, bool):
                        logger.warn('Expected for `%s` to be a boolean instead of `%r` (%s)', attr, value, type(value))
                        raise ValidationError(status_code.common.invalid_input, False)

            # All datetime objects must be actual Python datetime objects
            for attr in update.datetime_attrs:
                value = data.get(attr, _no_such_value)
                if value is not _no_such_value:
                    if not isinstance(value, datetime):
                        logger.warn('Expected for `%s` to be a datetime instead of `%r` (%s)', attr, value, type(value))
                        raise ValidationError(status_code.common.invalid_input, False)

            # Only certain attributes may be set to None / NULL
            for key, value in data.items():
                if value is None:
                    if key not in update.none_allowed:
                        logger.warn('Key `%s` must not be None', key)
                        raise ValidationError(status_code.common.invalid_input, False)

            # If approval_status is on input, it must be of correct value
            # and if it is, its related attributes need to bet set along with it.
            if 'approval_status' in data:
                value = data['approval_status']
                if value not in const.approval_status():
                    logger.warn('Invalid approval_status `%s`', value)
                    raise ValidationError(status_code.common.invalid_input, False)
                else:
                    data['approval_status_mod_by'] = current_session.user_id
                    data['approval_status_mod_time'] = _utcnow()

            # Everything is validated - we can save the data now
            with closing(self.odb_session_func()) as session:
                session.execute(
                    sql_update(UserModelTable).\
                    values(data).\
                    where(UserModelTable.c.user_id==_user_id)
                )
                session.commit()

# ################################################################################################################################

    def update_current_user(self, data, current_ust, current_app, remote_addr):
        """ Updates current user as identified by current_ust.
        """
        return self._update_user(data, current_ust, current_app, remote_addr, update_self=True)

# ################################################################################################################################

    def update_user_by_id(self, user_id, data, current_ust, current_app, remote_addr):
        """ Updates current user as identified by ID.
        """
        return self._update_user(data, current_ust, current_app, remote_addr, user_id=user_id)

# ################################################################################################################################

    def set_password(self, user_id, password, must_change, password_expiry, _utcnow=_utcnow):
        """ Sets a new password for user.
        """
        set_password(self.odb_session_func, self.encrypt_func, self.hash_func, self.sso_conf, user_id, password,
            must_change, password_expiry)

# ################################################################################################################################

    def change_password(self, data, current_ust, current_app, remote_addr):
        """ Changes a user's password. Super-admins may also set its expiration
        and whether the user must set it to a new one on next login.
        """
        # Basic checks first
        self._check_basic_update_attrs(data, change_password.max_len_attrs, change_password.all_attrs)

        # Get current user's session ..
        current_session = self._get_current_session(current_ust, current_app, remote_addr, needs_super_user=False)

        # . only super-users may send user_id on input ..
        user_id = data.get('user_id', _no_such_value)

        # .. so if it is sent ..
        if user_id != _no_such_value:

            # .. we must confirm we have a super-user's session.
            if not current_session.is_super_user:
                logger.warn('Current user `%s` is not a super-user, cannot change password for user `%s`',
                    current_session.user_id, user_id)
                raise ValidationError(status_code.common.invalid_input, False)

        # .. if ID is not given on input, we change current user's password.
        else:
            user_id = current_session.user_id

        # If current user is a super-user we can just set the new password immediately ..
        if current_session.is_super_user:

            # .. but only if the user changes another user's password ..
            if current_session.user_id != user_id:
                self.set_password(user_id, data['new_password'], data.get('must_change'), data.get('password_expiry'))

                # All done, another user's password has been changed
                return

        # .. otherwise, if we are a regular user or a super-user changing his or her own password,
        # so we must check first if the old password is correct.
        if not check_credentials(self.decrypt_func, self.verify_hash_func, current_session.password, data['old_password']):
            logger.warn('Password verification failed, user_id:`%s`', current_session.user_id)
            raise ValidationError(status_code.auth.not_allowed, True)
        else:

            # At this point we know that the user provided a correct old password so we are free to set the new one ..

            # .. but we still need to consider regular vs. super-users and make sure that the former does not
            # provide attributes that only the latter may use.

            # Super-users may provide these optionally ..
            if current_session.is_super_user:
                must_change = data.get('must_change')
                password_expiry = data.get('password_expiry')

            # .. but regular ones never.
            else:
                must_change = None
                password_expiry = None

            # All done, we can set the new password now.
            try:
                self.set_password(user_id, data['new_password'], must_change, password_expiry)
            except Exception:
                logger.warn('Could not set a new password for user_id:`%s`, e:`%s`', current_session.user_id, format_exc())
                raise ValidationError(status_code.auth.not_allowed, True)

# ################################################################################################################################

    def _change_approval_status(self, user_id, new_value, current_ust, current_app, remote_addr):
        """ Changes a given user's approval_status to 'value'.
        """
        return self._update_user({'approval_status': new_value}, current_ust, current_app, remote_addr, user_id=user_id)

# ################################################################################################################################

    def approve_user(self, user_id, current_ust, current_app, remote_addr):
        """ Changes a user's approval_status to 'approved'. Must be called with a UST pointing to a super-user.
        """
        return self._change_approval_status(user_id, const.approval_status.approved, current_ust, current_app, remote_addr)

# ################################################################################################################################

    def reject_user(self, user_id, current_ust, current_app, remote_addr):
        """ Changes a user's approval_status to 'approved'. Must be called with a UST pointing to a super-user.
        """
        return self._change_approval_status(user_id, const.approval_status.rejected, current_ust, current_app, remote_addr)

# ################################################################################################################################
