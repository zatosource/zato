# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy
from datetime import datetime, timedelta
from logging import getLogger
from traceback import format_exc
from uuid import uuid4

# gevent
from gevent.lock import RLock

# SQLAlchemy
from sqlalchemy import and_ as sql_and, update as sql_update
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.api import RATE_LIMIT, SEC_DEF_TYPE, TOTP
from zato.common.audit import audit_pii
from zato.common.crypto.api import CryptoManager
from zato.common.crypto.totp_ import TOTPManager
from zato.common.exception import BadRequest
from zato.common.json_internal import dumps
from zato.common.odb.model import SSOLinkedAuth as LinkedAuth, SSOSession as SessionModel, SSOUser as UserModel
from zato.sso import const, not_given, status_code, User as UserEntity, ValidationError
from zato.sso.attr import AttrAPI
from zato.sso.odb.query import get_linked_auth_list, get_sign_up_status_by_token, get_user_by_id, get_user_by_linked_sec, \
     get_user_by_name, get_user_by_ust
from zato.sso.session import LoginCtx, SessionAPI
from zato.sso.user_search import SSOSearch
from zato.sso.util import check_credentials, check_remote_app_exists, make_data_secret, make_password_secret, new_confirm_token, \
     set_password, validate_password

# ################################################################################################################################

if 0:
    from zato.common.odb.model import SSOSession
    from zato.common.typing_ import anydict, callable_, callnone
    from zato.server.base.parallel import ParallelServer
    from zato.sso.totp_ import TOTPAPI
    anydict = anydict
    callnone = callnone
    callable_ = callable_
    ParallelServer = ParallelServer
    TOTPAPI = TOTPAPI # type: ignore

# ################################################################################################################################

logger           = getLogger('zato')
logger_audit_pii = getLogger('zato_audit_pii')

# ################################################################################################################################

linked_auth_supported = SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.JWT

# ################################################################################################################################

sso_search = SSOSearch()
sso_search.set_up()

# ################################################################################################################################

_utcnow = datetime.utcnow

LinkedAuthTable = LinkedAuth.__table__
LinkedAuthTableDelete = LinkedAuthTable.delete

SessionModelTable = SessionModel.__table__
SessionModelTableDelete = SessionModelTable.delete

UserModelTable = UserModel.__table__
UserModelTableDelete = UserModelTable.delete
UserModelTableUpdate = UserModelTable.update

# ################################################################################################################################

# Attributes accessible to both account owner and super-users
regular_attrs = {
    'username': None,
    'email': b'',
    'display_name': '',
    'first_name': '',
    'middle_name': '',
    'last_name': '',
    'is_totp_enabled': False,
    'totp_label': '',
}

# Attributes accessible only to super-users
super_user_attrs = {
    'user_id': None,
    'is_active': False,
    'is_approval_needed': None,
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
    'is_rate_limit_active': None,
    'rate_limit_def': None,
    'rate_limit_type': None,
    'rate_limit_check_parent_def': None,
}

# This can be only changed but never read
_write_only = {
    'password': None,
}

# If any of these attributes exists on input to .update, its uppercased counterpart must also be updated
_name_attrs = {
    'display_name': 'display_name_upper',
    'first_name': 'first_name_upper',
    'middle_name': 'middle_name_upper',
    'last_name': 'last_name_upper'
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
    regular_attrs = {'username', 'email', 'display_name', 'first_name', 'middle_name', 'last_name', 'is_totp_enabled',
        'totp_label'}

    # Accessible to super-users only
    super_user_attrs = {'is_locked', 'password_expiry', 'password_must_change', 'sign_up_status', 'approval_status'}

    # All updateable attributes
    all_update_attrs = regular_attrs.union(super_user_attrs)

    # All updateable attributes + user_id
    all_attrs = all_update_attrs.union({'user_id'})

    # There cannot be more than this many attributes on input
    max_len_attrs = len(all_update_attrs)

    # All boolean attributes
    boolean_attrs = ('is_locked', 'password_must_change')

    # All datetime attributes
    datetime_attrs = ('password_expiry',)

    # All attributes that may be set to None / NULL
    none_allowed = set(regular_attrs) - {'username'}

# ################################################################################################################################

class change_password:

    # Accessible to regular users only
    regular_attrs = {'old_password', 'new_password'}

    # Accessible to super-users only
    super_user_attrs = {'new_password', 'password_expiry', 'password_must_change'}

    # This is used only for input validation which is why it is not called 'all_update_attrs'
    all_attrs = regular_attrs.union(super_user_attrs).union({'user_id'})

    # There cannot be more than this many attributes on input
    max_len_attrs = len(all_attrs)

# ################################################################################################################################

class Forbidden(Exception):
    def __init__(self, message='You are not authorized to access this resource'):
        super(Forbidden, self).__init__(message)

# ################################################################################################################################

class User:
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

class CreateUserCtx:
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

class UserAPI:
    """ The main object through SSO users are managed.
    """
    def __init__(
        self,
        server,           # type: ParallelServer
        sso_conf,         # type: anydict
        totp,             # type: TOTPAPI
        odb_session_func, # type: callable_
        encrypt_func,     # type: callable_
        decrypt_func,     # type: callable_
        hash_func,        # type: callable_
        verify_hash_func, # type: callable_
        new_user_id_func, # type: callnone
        ) -> 'None':

        self.server = server
        self.sso_conf = sso_conf
        self.totp = totp
        self.odb_session_func = odb_session_func
        self.is_sqlite = None
        self.encrypt_func = encrypt_func
        self.decrypt_func = decrypt_func
        self.hash_func = hash_func
        self.verify_hash_func = verify_hash_func
        self.new_user_id_func = new_user_id_func
        self.encrypt_email = self.sso_conf.main.encrypt_email
        self.encrypt_password = self.sso_conf.main.encrypt_password
        self.password_expiry = self.sso_conf.password.expiry
        self.lock = RLock()

        # To look up auth_user_id by auth_username or the other way around
        self.user_id_auth_type_func = {}
        self.user_id_auth_type_func_by_id = {}

        # In-RAM maps of auth IDs to SSO user IDs
        self.auth_id_link_map = {
            'zato.{}'.format(SEC_DEF_TYPE.BASIC_AUTH): {},
            'zato.{}'.format(SEC_DEF_TYPE.JWT): {}
        }

        # For convenience, sessions are accessible through user API.
        self.session = SessionAPI(self.server, self.sso_conf, self.totp, self.encrypt_func, self.decrypt_func, self.hash_func,
            self.verify_hash_func)

# ################################################################################################################################

    def post_configure(self, func, is_sqlite, needs_auth_link=True):
        self.odb_session_func = func
        self.is_sqlite = is_sqlite
        self.session.post_configure(func, is_sqlite)

        if needs_auth_link:

            # Maps all auth types that SSO users can be linked with to their server definitions
            self.auth_link_map = {
                SEC_DEF_TYPE.BASIC_AUTH: self.server.worker_store.request_dispatcher.url_data.basic_auth_config,
                SEC_DEF_TYPE.JWT: self.server.worker_store.request_dispatcher.url_data.jwt_config,
            }

            # This cannot be done in __init__ because it references the worker store
            self.user_id_auth_type_func[SEC_DEF_TYPE.BASIC_AUTH] = self.server.worker_store.basic_auth_get
            self.user_id_auth_type_func[SEC_DEF_TYPE.JWT] = self.server.worker_store.jwt_get

            self.user_id_auth_type_func_by_id[SEC_DEF_TYPE.BASIC_AUTH] = self.server.worker_store.basic_auth_get_by_id
            self.user_id_auth_type_func_by_id[SEC_DEF_TYPE.JWT] = self.server.worker_store.jwt_get_by_id

            # Load in initial mappings of SSO users and concrete security definitions
            with closing(self.odb_session_func()) as session:
                linked_auth_list = get_linked_auth_list(session)
                for item in linked_auth_list: # type: LinkedAuth
                    self._add_user_id_to_linked_auth(item.auth_type, item.auth_id, item.user_id)

# ################################################################################################################################

    def _get_encrypted_email(self, email):
        email = email or b''
        email = email.encode('utf8') if isinstance(email, str) else email
        return make_data_secret(email, self.encrypt_func)

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

        # If we still don't have any names, turn them all into NULLs
        for attr_name, attr_name_upper in _name_attrs.items():
            if not ctx.data[attr_name]:
                ctx.data[attr_name] = None
                ctx.data[attr_name_upper] = None

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
            ctx.data['password'], self.encrypt_password, self.encrypt_func, self.hash_func)

        # .. take into account the fact that emails are optional too ..
        email = ctx.data.get('email')

        #  .. emails are only encrypted, and whether to do it is optional ..
        if email and self.encrypt_email:
            email = self._get_encrypted_email(email)

        user_model.username = ctx.data['username']
        user_model.email = email

        user_model.password = password
        user_model.password_is_set = True
        user_model.password_last_set = now
        user_model.password_must_change = ctx.data.get('password_must_change') or False
        user_model.password_expiry = now + timedelta(days=self.password_expiry)

        totp_key = ctx.data.get('totp_key') or TOTPManager.generate_totp_key()
        totp_label = ctx.data.get('totp_label') or TOTP.default_label

        user_model.is_totp_enabled = ctx.data.get('is_totp_enabled')
        user_model.totp_key = self.encrypt_func(totp_key.encode('utf8'))
        user_model.totp_label = self.encrypt_func(totp_label.encode('utf8'))

        user_model.sign_up_status = ctx.data.get('sign_up_status')
        user_model.sign_up_time = now
        user_model.sign_up_confirm_token = ctx.data.get('sign_up_confirm_token') or new_confirm_token()

        user_model.approval_status = ctx.data['approval_status']
        user_model.approval_status_mod_time = now
        user_model.approval_status_mod_by = ctx.data['approval_status_mod_by']

        user_model.display_name = display_name
        user_model.first_name = ctx.data['first_name']
        user_model.middle_name = ctx.data['middle_name']
        user_model.last_name = ctx.data['last_name']

        user_model.is_rate_limit_active = ctx.data.get('is_rate_limit_active', False)
        user_model.rate_limit_type = ctx.data.get('rate_limit_type', RATE_LIMIT.TYPE.EXACT.id)
        user_model.rate_limit_def = ctx.data.get('rate_limit_def')
        user_model.rate_limit_check_parent_def = ctx.data.get('rate_limit_check_parent_def', False)

        # Uppercase any and all names for indexing purposes.
        for attr_name, attr_name_upper in _name_attrs.items():
            value = ctx.data[attr_name]
            if value:
                setattr(user_model, attr_name_upper, value.upper())

        return user_model

# ################################################################################################################################

    def _require_super_user(self, cid, ust, current_app, remote_addr):
        """ Raises an exception if either current user session token does not belong to a super user.
        """
        return self._get_current_session(cid, ust, current_app, remote_addr, needs_super_user=True)

# ################################################################################################################################

    def _create_user(self, ctx, cid, is_super_user, ust=None, current_app=None, remote_addr=None, require_super_user=True,
        auto_approve=False):
        """ Creates a new regular or super-user out of initial user data.
        """
        with closing(self.odb_session_func()) as session:

            if require_super_user:
                current_session = self._require_super_user(cid, ust, current_app, remote_addr)
                current_user = current_session.user_id
            else:
                current_user = 'auto'

            ctx.data['approval_status_mod_by'] = current_user

            if auto_approve:
                approval_status = const.approval_status.approved
            else:
                if self.sso_conf.signup.is_approval_needed:
                    approval_status = const.approval_status.before_decision
                else:
                    approval_status = const.approval_status.approved

            ctx.data['approval_status'] = approval_status

            # The only field always required
            if not ctx.data.get('username'):
                logger.warning('Missing `username` on input')
                raise ValidationError(status_code.username.invalid, True)

            # Make sure the username is unique
            if get_user_by_name(session, ctx.data['username'], needs_approved=False):
                logger.warning('Username `%s` already exists', ctx.data['username'])
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
            ctx.data['approval_status'] = approval_status
            ctx.data['approval_status_mod_time'] = user.approval_status_mod_time
            ctx.data['approval_status_mod_by'] = user.approval_status_mod_by
            ctx.data['is_approval_needed'] = approval_status != const.approval_status.approved
            ctx.data['is_locked'] = user.is_locked
            ctx.data['is_super_user'] = user.is_super_user
            ctx.data['password_is_set'] = user.password_is_set
            ctx.data['password_last_set'] = user.password_last_set
            ctx.data['password_must_change'] = user.password_must_change
            ctx.data['password_expiry'] = user.password_expiry
            ctx.data['sign_up_status'] = user.sign_up_status
            ctx.data['sign_up_time'] = user.sign_up_time
            ctx.data['is_totp_enabled'] = user.is_totp_enabled
            ctx.data['totp_label'] = user.totp_label

            # This one we do not want to reveal back
            ctx.data.pop('password', None)

            session.add(user)
            session.commit()

            user_id = user.user_id

        return user_id

# ################################################################################################################################

    def create_user(self, cid, data, ust=None, current_app=None, remote_addr=None, require_super_user=True, auto_approve=False):
        """ Creates a new regular user.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.create_user', extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._create_user(CreateUserCtx(data), cid, False, ust, current_app, remote_addr, require_super_user, auto_approve)

# ################################################################################################################################

    def create_super_user(self, cid, data, ust=None, current_app=None, remote_addr=None, require_super_user=True,
        auto_approve=False):
        """ Creates a new super-user.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.create_super_user', extra={'current_app':current_app, 'remote_addr':remote_addr})

        # Super-users don't need to confirmation their own creation
        data['sign_up_status'] = const.signup_status.final

        return self._create_user(CreateUserCtx(data), cid, True, ust, current_app, remote_addr, require_super_user, auto_approve)

# ################################################################################################################################

    def signup(self, cid, ctx, current_app, remote_addr):
        """ Signs up a user with SSO, assuming that all validation services confirm correctness of input data.
        On success, invokes callback services interested in the signup process.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.signup', extra={'current_app':current_app, 'remote_addr':remote_addr})

        # There is no current user so we cannot do more than only confirm that current_app truly exists.
        self._ensure_app_exists(current_app)

        # Used to confirm by users that an account should be really opened
        confirm_token = new_confirm_token()

        # Neeed in a couple of places below
        ctx_dict = ctx.to_dict()
        ctx_dict['sign_up_confirm_token'] = confirm_token

        for name in self.sso_conf.user_validation.service:
            validation_response = self.server.invoke(name, ctx_dict, serialize=False)
            if not validation_response['is_valid']:
                raise ValidationError(validation_response['sub_status'])

        # None of validation services returned an error so we can create the user now
        self.create_user(cid, ctx_dict, current_app=current_app, remote_addr=remote_addr, require_super_user=False)

        # Invoke all callback services interested in the event of user's signup
        for name in self.sso_conf.signup.callback_service_list:
            self.server.invoke(name, ctx_dict)

        return confirm_token

# ################################################################################################################################

    def confirm_signup(self, cid, confirm_token, current_app, remote_addr, _utcnow=_utcnow):
        """ Invoked when users want to confirm their signup with the system.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.confirm_signup', extra={'current_app':current_app, 'remote_addr':remote_addr})

        # There is no current user so we cannot do more than only confirm that current_app truly exists.
        self._ensure_app_exists(current_app)

        with closing(self.odb_session_func()) as session:

            sign_up_status = get_sign_up_status_by_token(session, confirm_token)

            # No such token, raise an exception then ..
            if not sign_up_status:
                raise ValidationError(status_code.auth.no_such_sign_up_token)

            # .. cannot confirm signup processes that are not before confirmation ..
            elif sign_up_status[0] != const.signup_status.before_confirmation:
                raise ValidationError(status_code.auth.sign_up_confirmed)

            # .. OK, found a valid token ..
            else:

                # .. set signup metadata ..
                session.execute(
                    UserModelTableUpdate().values({
                        'sign_up_status': const.signup_status.final,
                        'sign_up_confirm_time': _utcnow(),
                }).where(
                    UserModelTable.c.sign_up_confirm_token==confirm_token
                ))

                # .. and commit it to DB.
                session.commit()

# ################################################################################################################################

    def get_user_by_username(self, cid, username, needs_approved=True):
        """ Returns a user object by username or None, if there is no such username.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.get_user_by_username', extra={'username':username})

        with closing(self.odb_session_func()) as session:
            return get_user_by_name(session, username, needs_approved=needs_approved)

# ################################################################################################################################

    def _get_current_session(
        self,
        cid,         # type: str
        current_ust, # type: str
        current_app, # type: str
        remote_addr, # type: str
        needs_super_user, # type: bool
        ) -> 'SSOSession':
        """ Returns current session info or raises an exception if it could not be found.
        Optionally, requires that a super-user be owner of current_ust.
        """
        return self.session.get_current_session(cid, current_ust, current_app, remote_addr, needs_super_user)

# ################################################################################################################################

    def _get_user(self, cid, func, query_criteria, current_ust, current_app, remote_addr, _needs_super_user,
        queries_current_session, return_all_attrs, _utcnow=_utcnow):
        """ Returns a user by a specific function and business value.
        """
        with closing(self.odb_session_func()) as session:

            # Validate and get session
            current_session = self._get_current_session(cid, current_ust, current_app, remote_addr, _needs_super_user)

            # If func was to query current session, we can just re-use what we have fetched above,
            # so as to have one SQL query less in a piece of code that will be likely used very often.
            if queries_current_session:
                info = current_session
            else:
                info = func(session, query_criteria, _utcnow())

            # Input UST is invalid for any reason (perhaps it has just expired), raise an exception in that case
            if not info:
                raise ValidationError(status_code.auth.not_allowed, True)

            # UST is valid, let's return data then
            else:

                # Main user entity
                out = UserEntity()
                out.is_current_super_user = current_session.is_super_user

                access_msg = 'Cid:%s. Accessing %s user attrs (s:%d, r:%d).'

                if current_session.is_super_user or return_all_attrs:
                    logger_audit_pii.info(access_msg, cid, 'all', current_session.is_super_user, return_all_attrs)

                    # This will suffice for 99% of purposes ..
                    attrs = _all_super_user_attrs

                    # .. but to return this, it does not suffice to be a super-user,
                    # .. we need to be requested to do it explicitly via this flag.
                    if return_all_attrs:
                        attrs['totp_key'] = None
                    out.is_approval_needed = self.sso_conf.signup.is_approval_needed
                else:
                    logger_audit_pii.info(access_msg, cid, 'regular', current_session.is_super_user, return_all_attrs)
                    attrs = regular_attrs

                for key in attrs:

                    value = getattr(info, key, None)

                    if key == 'is_approval_needed':
                        value = value or False

                    if isinstance(value, datetime):
                        value = value.isoformat()

                    # This will be encrypted ..
                    elif key in ('totp_key', 'totp_label'):
                        value = self.decrypt_func(value)

                        # .. do not return our internal constant if no label has been assign to TOTP.
                        if key == 'totp_label':
                            if value == TOTP.default_label:
                                value = ''

                    setattr(out, key, value)

                if out.email:
                    if self.sso_conf.main.encrypt_email:
                        try:
                            out.email = self.decrypt_func(out.email)
                        except Exception:
                            logger.warning('Could not decrypt email, user_id:`%s` (%s)', out.user_id, format_exc())

                # Custom attributes
                out.attr = AttrAPI(cid, current_session.user_id, current_session.is_super_user, current_app, remote_addr,
                    self.odb_session_func, self.is_sqlite, self.encrypt_func, self.decrypt_func, info.user_id)

                return out

# ################################################################################################################################

    def get_current_user(self, cid, current_ust, current_app, remote_addr, return_all_attrs=False):
        """ Returns a user object by that person's current UST.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.get_current_user', extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._get_user(
            cid, get_user_by_ust, self.decrypt_func(current_ust), current_ust, current_app, remote_addr,
            _needs_super_user=False,
            queries_current_session=True,
            return_all_attrs=return_all_attrs
        )

# ################################################################################################################################

    def get_user_by_id(self, cid, user_id, current_ust, current_app, remote_addr, return_all_attrs=False):
        """ Returns a user object by that person's ID.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.get_user_by_id', target_user=user_id,
            extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._get_user(cid, get_user_by_id, user_id, current_ust, current_app, remote_addr,
            _needs_super_user=True,
            queries_current_session=False,
            return_all_attrs=return_all_attrs
        )

# ################################################################################################################################

    def get_user_by_linked_auth(self, cid, sec_type, sec_username, current_ust, current_app, remote_addr, return_all_attrs=False):
        """ Returns a user object by that person's linked security name, e.g. maps a Basic Auth username to an SSO user.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.get_user_by_linked_sec', target_user=sec_username,
            extra={'current_app':current_app, 'remote_addr':remote_addr, 'sec_type': sec_type})

        return self._get_user(
            cid, get_user_by_linked_sec, (sec_type, sec_username), current_ust, current_app, remote_addr,
            _needs_super_user=False,
            queries_current_session=True,
            return_all_attrs=return_all_attrs
        )

# ################################################################################################################################

    def validate_password(self, password):
        return validate_password(self.sso_conf, password)

# ################################################################################################################################

    def _delete_user(self, cid, user_id, username, current_ust, current_app, remote_addr, skip_sec=False):
        """ Deletes a user by ID or username.
        """
        if not skip_sec:
            current_session = self._get_current_session(cid, current_ust, current_app, remote_addr, needs_super_user=False)
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
                user = get_user_by_name(session, username, needs_approved=False)
                where = UserModelTable.c.username==username

            user_id = user.user_id

            # Make sure the user exists at all
            if not user:
                raise ValidationError(status_code.common.invalid_operation, False)

            # Users cannot delete themselves
            if not skip_sec:
                if user_id == current_session.user_id:
                    raise ValidationError(status_code.common.invalid_operation, False)

            rows_matched = session.execute(
                UserModelTableDelete().\
                where(where)
            ).rowcount
            session.commit()

            if rows_matched != 1:
                msg = 'Expected for rows_matched to be 1 instead of %d, user_id:`%s`, username:`%s`'
                logger.warning(msg, rows_matched, user_id, username)

            # After deleting the user from ODB, we can remove a reference to this account
            # from the map of linked accounts.
            for auth_id_link_map in self.auth_id_link_map.values(): # type: dict
                to_delete = set()

                for sso_user_id in auth_id_link_map.values():
                    if user_id == sso_user_id:
                        to_delete.add(user_id)

                for user_id in to_delete:
                    del auth_id_link_map[user_id]

# ################################################################################################################################

    def delete_user_by_id(self, cid, user_id, current_ust, current_app, remote_addr, skip_sec=False):
        """ Deletes a user by that person's ID.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.delete_user_by_id', target_user=user_id,
            extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._delete_user(cid, user_id, None, current_ust, current_app, remote_addr, skip_sec)

# ################################################################################################################################

    def delete_user_by_username(self, cid, username, current_ust, current_app, remote_addr, skip_sec=False):
        """ Deletes a user by that person's username.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.delete_user_by_username', extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._delete_user(cid, None, username, current_ust, current_app, remote_addr, skip_sec)

# ################################################################################################################################

    def lock_user(self, cid, user_id, current_ust=None, current_app=None, remote_addr=None, require_super_user=True,
        current_user=None):
        """ Locks an existing user. It is acceptable to lock an already lock user.
        """
        # type: (str, str, str, str, str, bool, str)

        # PII audit comes first
        audit_pii.info(cid, 'user.lock_user', extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._lock_user(user_id, True, cid, current_ust, current_app, remote_addr, require_super_user, current_user)

# ################################################################################################################################

    def unlock_user(self, cid, user_id, current_ust=None, current_app=None, remote_addr=None, require_super_user=True,
        current_user=None):
        """ Unlocks an existing user. It is acceptable to unlock a user that is not locked.
        """
        # type: (str, str, str, str, str, bool, str)

        # PII audit comes first
        audit_pii.info(cid, 'user.lock_user', extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._lock_user(user_id, False, cid, current_ust, current_app, remote_addr, require_super_user, current_user)

# ################################################################################################################################

    def _lock_user(self, user_id, is_locked, cid=None, current_ust=None, current_app=None, remote_addr=None,
        require_super_user=True, current_user=None):
        """ An internal method to lock or unlock users.
        """
        # type: (str, bool, str, str, str, str, bool, str)
        if require_super_user:
            current_session = self._require_super_user(cid, current_ust, current_app, remote_addr)
            current_user = current_session.user_id
        else:
            current_user = current_user if current_user else 'auto'

        # We have all that is needed to so we can actually issue the SQL call.
        # Note that we always populate locked_time and locked_by even if is_locked is False
        # to keep track of both who locked and unlocked the user.
        with closing(self.odb_session_func()) as session:
            session.execute(
                sql_update(UserModelTable).\
                values({
                    'is_locked': is_locked,
                    'locked_time': datetime.utcnow(),
                    'locked_by': current_user,
                    }).\
                where(UserModelTable.c.user_id==user_id)
            )
            session.commit()

# ################################################################################################################################

    def login(self, cid, username, password, current_app, remote_addr, user_agent=None,
        has_remote_addr=False, has_user_agent=False, new_password='', totp_code=None, skip_sec=False):
        """ Logs a user in if username and password are correct, returning a user session token (UST) on success,
        or a ValidationError on error.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.login', target_user=username, extra={
            'current_app': current_app,
            'remote_addr': remote_addr,
            'user_agent': user_agent,
            'new_password': bool(new_password) # To store information if a new password was sent or not
        })

        ctx_input = {
          'username': username,
          'password': password,
          'current_app': current_app,
          'new_password': new_password,
          'totp_code': totp_code,
        }
        login_ctx = LoginCtx(cid, remote_addr, user_agent, ctx_input)
        return self.session.login(login_ctx, is_logged_in_ext=False, skip_sec=skip_sec)

# ################################################################################################################################

    def logout(self, cid, ust, current_app, remote_addr, skip_sec=False):
        """ Logs a user out of SSO.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.logout', extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self.session.logout(ust, current_app, remote_addr, skip_sec=skip_sec)

# ################################################################################################################################

    def _ensure_app_exists(self, app):
        """ Raises an exception if input does not exist in SSO configuration.
        """
        check_remote_app_exists(app, self.sso_conf.apps.all, logger)

# ################################################################################################################################

    def _ensure_no_unknown_update_attrs(self, attrs_allowed, data):
        """ Makes sure that update data contains only attributes explicitly allowed.
        """
        unexpected = []
        for attr in data:
            if attr not in attrs_allowed:
                unexpected.append(attr)

        if unexpected:
            logger.warning('Unexpected data on input %s', unexpected)
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
                logger.warning('Too many data arguments %d > %d', len(data), max_len_attrs)
                raise ValidationError(status_code.common.invalid_input, False)

            # .. also, make sure that, no matter what kind of user this is, only supported arguments are given on input.
            # Later on we will fine-check it again to take the user's role into account, but we want to want to check it here
            # first on a rough level so as to avoid an SQL query in case of an error at this early stage.
            else:
                self._ensure_no_unknown_update_attrs(all_update_attrs, data)

# ################################################################################################################################

    def _update_user(self, cid, data, current_ust, current_app, remote_addr, user_id=None, update_self=None):
        """ Low-level implementation of user updates.
        """
        if not(user_id or update_self):
            logger.warning('At least one of user_id or update_self is required')
            raise ValidationError(status_code.common.invalid_input, False)

        # Basic checks first
        self._check_basic_update_attrs(data, update.max_len_attrs, update.all_update_attrs)

        with closing(self.odb_session_func()) as session:
            current_session = self._get_current_session(cid, current_ust, current_app, remote_addr, needs_super_user=False)

            # We will be updating our own account or another user, depending on input flags/parameters.
            _user_id = current_session.user_id if update_self else user_id

            # Super-users may update the whole set of attributes in existence.
            if current_session.is_super_user:
                attrs_allowed = update.all_update_attrs
            else:

                # If current session belongs to a regular user yet a user_id was given on input,
                # we may not continue because only super-users may update other users
                if user_id and user_id != current_session.user_id:
                    logger.warning('Current user `%s` is not a super-user, cannot update user `%s`',
                        current_session.user_id, user_id)
                    raise ValidationError(status_code.common.invalid_input, False)

                # Regular users may change only basic attributes
                attrs_allowed = update.regular_attrs

            # Make sure current user provided only these attributes that have been explicitly allowed
            self._ensure_no_unknown_update_attrs(attrs_allowed, data)

            # If username is to be changed, we need to ensure that such a username is not used by another user
            username = data.get('username') # type: str

            # We have a username in put ..
            if username:

                # .. now, we can check whether that username is already in use ..
                existing_user = get_user_by_name(session, username, False) # type: UserModel

                # .. if it does ..
                if existing_user:

                    # .. and if the other user is not the same that we are editing ..
                    if existing_user.user_id != _user_id:

                        # .. we need to reject the new username.
                        logger.warning('Username `%s` already exists (update)',username)
                        raise ValidationError(status_code.username.exists, False)

            # If sign_up_status was given on input, it must be among allowed values
            sign_up_status = data.get('sign_up_status')
            if sign_up_status and sign_up_status not in const.signup_status():
                logger.warning('Invalid sign_up_status `%s`', sign_up_status)
                raise ValidationError(status_code.common.invalid_input, False)

            # All booleans must be actually booleans
            for attr in update.boolean_attrs:
                value = data.get(attr, _no_such_value)
                if value is not _no_such_value:
                    if not isinstance(value, bool):
                        logger.warning('Expected for `%s` to be a boolean instead of `%r` (%s)', attr, value, type(value))
                        raise ValidationError(status_code.common.invalid_input, False)

            # All datetime objects must be actual Python datetime objects
            for attr in update.datetime_attrs:
                value = data.get(attr, _no_such_value)
                if value is not _no_such_value:
                    if not isinstance(value, datetime):
                        logger.warning('Expected for `%s` to be a datetime instead of `%r` (%s)', attr, value, type(value))
                        raise ValidationError(status_code.common.invalid_input, False)

            # Only certain attributes may be set to None / NULL
            for key, value in data.items():
                if value is None:
                    if key not in update.none_allowed:
                        logger.warning('Key `%s` must not be None', key)
                        raise ValidationError(status_code.common.invalid_input, False)

            # If approval_status is on input, it must be of correct value
            # and if it is, its related attributes need to bet set along with it.
            if 'approval_status' in data:
                value = data['approval_status']
                if value not in const.approval_status():
                    logger.warning('Invalid approval_status `%s`', value)
                    raise ValidationError(status_code.common.invalid_input, False)
                else:
                    data['approval_status_mod_by'] = current_session.user_id
                    data['approval_status_mod_time'] = _utcnow()

            # Uppercase or remove attributes that are later on used for search
            for attr_name, attr_name_upper in _name_attrs.items():
                if attr_name in data:
                    if attr_name is None:
                        data[attr_name_upper] = None
                    else:
                        if attr_name and isinstance(data[attr_name], str):
                            data[attr_name_upper] = data[attr_name].upper()

            # Email may be optionally encrypted
            if self.encrypt_email:
                email = data.get('email')
                if email:
                    data['email'] = self._get_encrypted_email(email)

            # Everything is validated - we can save the data now
            with closing(self.odb_session_func()) as session:
                session.execute(
                    sql_update(UserModelTable).\
                    values(data).\
                    where(UserModelTable.c.user_id==_user_id)
                )

                session.commit()

# ################################################################################################################################

    def update_current_user(self, cid, data, current_ust, current_app, remote_addr):
        """ Updates current user as identified by current_ust.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.update_current_user', extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._update_user(cid, data, current_ust, current_app, remote_addr, update_self=True)

# ################################################################################################################################

    def update_user_by_id(self, cid, user_id, data, current_ust, current_app, remote_addr):
        """ Updates current user as identified by ID.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.update_user_by_id', target_user=user_id,
            extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._update_user(cid, data, current_ust, current_app, remote_addr, user_id=user_id)

# ################################################################################################################################

    def set_password(self, cid, user_id, password, must_change, password_expiry, current_app, remote_addr, details=None):
        """ Sets a new password for user.
        """
        # PII audit comes first
        extra = {'current_app':current_app, 'remote_addr':remote_addr}

        if details:
            extra.update(details)

        audit_pii.info(cid, 'user.set_password', target_user=user_id, extra=extra)

        set_password(self.odb_session_func, self.encrypt_func, self.hash_func, self.sso_conf, user_id, password,
            must_change, password_expiry)

# ################################################################################################################################

    def reset_totp_key(self, cid, current_ust, user_id, key, key_label, current_app, remote_addr, skip_sec=False):
        """ Saves a new TOTP key for user, either using the one provided on input or a newly generated one.
        In the latter case, it is also returned on output.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.reset_totp_key', target_user=user_id,
            extra={
                'current_app': current_app,
                'remote_addr': remote_addr,
                'skip_sec': skip_sec,
                'user_id': user_id,
            })

        key = key or CryptoManager.generate_totp_key()
        key_label = key_label or TOTP.default_label

        # Flag skip_sec will be True if we are being called from CLI,
        # in which case we are allowed to set the key for any user.
        # Otherwise, regular users may change their own keys only
        # while super-users may change any other user's key.

        if skip_sec:
            _user_id = user_id
        else:

            # Get current session by its UST ..
            current_session = self._get_current_session(cid, current_ust, current_app, remote_addr, needs_super_user=False)

            # .. if user_id is given, reject the request if it does not belong to a super-user ..
            if user_id:

                # A non-super-user tries to reset TOTP key of another user
                if not current_session.is_super_user:
                    logger.warning('Current user `%s` is not a super-user, cannot reset TOTP key for user `%s`',
                        current_session.user_id, user_id)
                    raise ValidationError(status_code.common.invalid_input, False)

                # This is good, it is a super-user resetting the TOTP key
                else:

                    # We need to confirm that such a user exists
                    if not self.get_user_by_id(cid, user_id, current_ust, current_app, remote_addr):
                        logger.warning('No such user `%s`', user_id)
                        raise ValidationError(status_code.common.invalid_input, False)

                    # Input user actually exists
                    else:
                        _user_id = user_id

            # .. no user_id given on input, which means we reset the current user's TOTP key
            else:
                _user_id = current_session.user_id

        # Data to be saved comprises the TOTP key in an encrypted form
        # along with its label, alco encrypted.
        data = {
            'totp_key': self.encrypt_func(key.encode('utf8')),
            'totp_label': self.encrypt_func(key_label.encode('utf8')),
        }

        # Everything is ready - we can save the data now
        with closing(self.odb_session_func()) as session:
            session.execute(
                sql_update(UserModelTable).\
                values(data).\
                where(UserModelTable.c.user_id==_user_id)
            )
            session.commit()

        return key

# ################################################################################################################################

    def change_password(self, cid, data, current_ust, current_app, remote_addr, _no_user_id='no-user-id.{}'.format(uuid4().hex)):
        """ Changes a user's password. Super-admins may also set its expiration
        and whether the user must set it to a new one on next login.
        """
        # Basic checks first
        self._check_basic_update_attrs(data, change_password.max_len_attrs, change_password.all_attrs)

        # Get current user's session ..
        current_session = self._get_current_session(cid, current_ust, current_app, remote_addr, needs_super_user=False)

        # . only super-users may send user_id on input ..
        user_id = data.get('user_id', _no_user_id)

        # PII audit goes here, once we know the target user's ID
        audit_pii.info(
            cid, 'user.change_password', target_user=user_id, extra={'current_app':current_app, 'remote_addr':remote_addr})

        # .. so if it is sent ..
        if user_id != _no_user_id:

            # .. and we are not changing our own password ..
            if current_session.user_id != user_id:

                # .. we must confirm we have a super-user's session.
                if not current_session.is_super_user:
                    logger.warning('Current user `%s` is not a super-user, cannot change password for user `%s`',
                        current_session.user_id, user_id)
                    raise ValidationError(status_code.common.invalid_input, False)

        # .. if ID is not given on input, we change current user's password.
        else:
            user_id = current_session.user_id

        # If current user is a super-user we can just set the new password immediately ..
        if current_session.is_super_user:

            # .. but only if the user changes another user's password ..
            if current_session.user_id != user_id:
                self.set_password(cid, user_id, data['new_password'], data.get('must_change'), data.get('password_expiry'),
                    current_app, remote_addr)

                # All done, another user's password has been changed
                return

        # .. otherwise, if we are a regular user or a super-user changing his or her own password,
        # so we must check first if the old password is correct.
        if not check_credentials(self.decrypt_func, self.verify_hash_func, current_session.password, data['old_password']):
            logger.warning('Password verification failed, user_id:`%s`', current_session.user_id)
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
                self.set_password(cid, user_id, data['new_password'], must_change, password_expiry, current_app, remote_addr)
            except Exception:
                logger.warning('Could not set a new password for user_id:`%s`, e:`%s`', current_session.user_id, format_exc())
                raise ValidationError(status_code.auth.not_allowed, True)

# ################################################################################################################################

    def _change_approval_status(self, cid, user_id, new_value, current_ust, current_app, remote_addr):
        """ Changes a given user's approval_status to 'value'.
        """
        return self._update_user(cid, {'approval_status': new_value}, current_ust, current_app, remote_addr, user_id=user_id)

# ################################################################################################################################

    def approve_user(self, cid, user_id, current_ust, current_app, remote_addr):
        """ Changes a user's approval_status to 'approved'. Must be called with a UST pointing to a super-user.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.approve_user', target_user=user_id,
            extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._change_approval_status(cid, user_id, const.approval_status.approved, current_ust, current_app, remote_addr)

# ################################################################################################################################

    def reject_user(self, cid, user_id, current_ust, current_app, remote_addr):
        """ Changes a user's approval_status to 'approved'. Must be called with a UST pointing to a super-user.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.reject_user', target_user=user_id, extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self._change_approval_status(cid, user_id, const.approval_status.rejected, current_ust, current_app, remote_addr)

# ################################################################################################################################

    def get_linked_auth_list(self, cid, ust, current_app, remote_addr, user_id=None):
        """ Returns a list of linked auth accounts for input user, either current or another one.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.get_linked_auth_list', extra={'current_app':current_app, 'remote_addr':remote_addr})

        # Get current user, which may be possibly the one that we will return accounts for
        user = self.get_current_user(cid, ust, current_app, remote_addr)

        # We are to return linked accounts for another user ..
        if user_id:

            # .. in which case this will raise an exception if current caller is not a super-user
            self._require_super_user(cid, ust, current_app, remote_addr)

        else:
            # No user_id given on input = we need to get accounts for current one
            user_id = user.user_id

        try:
            with closing(self.odb_session_func()) as session:
                out = []
                auth_list = get_linked_auth_list(session, user_id)

                for item in auth_list:
                    item = item._asdict()
                    item['auth_type'] = item['auth_type'].replace('zato.', '', 1)
                    auth_func = self.user_id_auth_type_func_by_id[item['auth_type']]

                    auth_config = auth_func(item['auth_id'])
                    auth_username = auth_config['username']

                    item['auth_username'] = auth_username
                    out.append(item)

                return out
        except Exception:
            logger.warning('Could not return linked accounts, e:`%s`', format_exc())

# ################################################################################################################################

    def _check_linked_auth_call(self, call_name, cid, ust, user_id, auth_type, auth_id, current_app, remote_addr,
        _linked_auth_supported=linked_auth_supported):

        # PII audit comes first
        audit_pii.info(cid, call_name, extra={'current_app':current_app, 'remote_addr':remote_addr})

        # Only super-users may link auth accounts
        self._require_super_user(cid, ust, current_app, remote_addr)

        if auth_type not in self.auth_link_map:
            raise ValueError('Invalid auth_type:`{}`'.format(auth_type))

        for item in self.auth_link_map[auth_type].values(): # type: dict
            config = item['config']
            if config['id'] == auth_id:
                break
        else:
            raise ValueError('Invalid auth_id:`{}`'.format(auth_id))

# ################################################################################################################################

    def _get_auth_username_by_id(self, cid, auth_type, auth_username, _linked_auth_supported=linked_auth_supported):

        # Confirm that input auth_type if of the allowed type
        if auth_type not in _linked_auth_supported:
            raise BadRequest(cid, 'Invalid auth_type `{}`'.format(auth_type))

        # Input auth_username is the linked account's username
        # and we need to translate it into its underlying auth_id
        # which is what the SSO API expects.

        func = self.user_id_auth_type_func[auth_type]
        auth_config = func(auth_username)

        if not auth_config:
            raise BadRequest(cid, 'Invalid auth_username ({})'.format(auth_type))
        else:
            auth_user_id = auth_config['config']['id']
            return auth_user_id

# ################################################################################################################################

    def create_linked_auth(self, cid, ust, user_id, auth_type, auth_username, is_active, current_app, remote_addr,
        _linked_auth_supported=linked_auth_supported):
        """ Creates a link between input user and a security account.
        """
        # Convert auth_username to auth_id, if it exists
        auth_id = self._get_auth_username_by_id(cid, auth_type, auth_username)

        # Validate input
        self._check_linked_auth_call('user.create_linked_auth', cid, ust, user_id, auth_type, auth_id, current_app, remote_addr)

        # We have validated everything and a link can be saved to the database now
        now = datetime.utcnow()
        auth_type = 'zato.{}'.format(auth_type)

        with closing(self.odb_session_func()) as session:

            instance = LinkedAuth()
            instance.auth_id = auth_id
            instance.auth_type = auth_type
            instance.creation_time = now
            instance.last_modified = now
            instance.is_internal = False
            instance.is_active = is_active
            instance.user_id = user_id

            # Reserved for future use
            instance.has_ext_principal = False
            instance.auth_principal = 'reserved'
            instance.auth_source = 'reserved'

            session.add(instance)

            try:
                session.commit()
            except IntegrityError:
                logger.warning('Could not add auth link e:`%s`', format_exc())
                raise ValueError('Auth link could not be added')
            else:
                self._add_user_id_to_linked_auth(auth_type, auth_id, user_id)
                return instance.user_id, auth_id

# ################################################################################################################################

    def delete_linked_auth(self, cid, ust, user_id, auth_type, auth_username, current_app, remote_addr,
        _linked_auth_supported=linked_auth_supported):
        """ Creates a link between input user and a security account.
        """
        # Convert auth_username to auth_id, if it exists
        auth_id = self._get_auth_username_by_id(cid, auth_type, auth_username)

        # Validate input
        self._check_linked_auth_call('user.delete_linked_auth', cid, ust, user_id, auth_type, auth_id, current_app, remote_addr)

        # All internal auth types have this prefix
        zato_auth_type = 'zato.{}'.format(auth_type)

        with closing(self.odb_session_func()) as session:

            # First, confirm that such a mapping exists at all ..
            existing = session.query(LinkedAuth).\
                filter(LinkedAuth.auth_type==zato_auth_type).\
                filter(LinkedAuth.auth_id==auth_id).\
                filter(LinkedAuth.user_id==user_id).\
                first()

            if not existing:
                raise ValueError('No such auth link found')

            # .. delete it now, knowing that it does ..
            session.execute(LinkedAuthTableDelete().\
                where(sql_and(
                    LinkedAuthTable.c.auth_type==zato_auth_type,
                    LinkedAuthTable.c.auth_id==auth_id,
                    LinkedAuthTable.c.user_id==user_id,
                ))
            )

            # .. delete any sessions possibly existing for this link ..
            session.execute(SessionModelTableDelete().\
                where(sql_and(
                    SessionModelTable.c.ext_session_id.startswith('{}.{}'.format(auth_type, auth_id)),
                ))
            )

            session.commit()

        return auth_id

# ################################################################################################################################

    def _add_user_id_to_linked_auth(self, auth_type, auth_id, user_id):
        self.auth_id_link_map[auth_type].setdefault(auth_id, user_id)

# ################################################################################################################################

    def on_broker_msg_SSO_LINK_AUTH_CREATE(self, auth_type, auth_id, user_id):
        with self.lock:
            self._add_user_id_to_linked_auth(auth_type, auth_id, user_id)

# ################################################################################################################################

    def on_broker_msg_SSO_LINK_AUTH_DELETE(self, auth_type, auth_id):

        auth_type = 'zato.{}'.format(auth_type)

        with self.lock:
            auth_id_link_map = self.auth_id_link_map[auth_type]
            try:
                del auth_id_link_map[auth_id]
            except KeyError:
                # It is fine, the user had not linked accounts
                pass

# ################################################################################################################################

    def _on_broker_msg_sec_delete(self, sec_type, auth_id):
        auth_id_link_map = self.auth_id_link_map['zato.{}'.format(sec_type)]
        try:
            del auth_id_link_map[auth_id]
        except KeyError:
            # It is fine, the account had no associated SSO users
            pass

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_DELETE(self, auth_id):
        with self.lock:
            self._on_broker_msg_sec_delete(SEC_DEF_TYPE.BASIC_AUTH, auth_id)

# ################################################################################################################################

    def on_broker_msg_SECURITY_JWT_DELETE(self, auth_id):
        with self.lock:
            self._on_broker_msg_sec_delete(SEC_DEF_TYPE.JWT, auth_id)

# ################################################################################################################################

    def search(self, cid, ctx, current_ust, current_app, remote_addr, serialize_dt=False,
        _all_super_user_attrs=_all_super_user_attrs,
        _dt=('sign_up_time', 'password_expiry', 'approv_rej_time', 'locked_time', 'approval_status_mod_time')):
        """ Looks up users by specific search criteria from the SearchCtx ctx object.
        Must be called with a UST belonging to a super-user.
        """
        # PII audit comes first
        audit_pii.info(cid, 'user.search', extra={'current_app':current_app, 'remote_addr':remote_addr})

        # Will raise an exception if current user is not an admin
        current_session = self._get_current_session(cid, current_ust, current_app, remote_addr, needs_super_user=True)

        if ctx.cur_page < 1:
            ctx.cur_page = 1

        if (not ctx.page_size) or (ctx.page_size < 1):
            ctx.page_size = self.sso_conf.search.default_page_size

        elif ctx.page_size > self.sso_conf.search.max_page_size:
            ctx.page_size = self.sso_conf.search.max_page_size

        # Local alias, useful in decryption of emails later on
        is_email_encrypted = self.sso_conf.main.encrypt_email

        config = {
            'paginate': ctx.paginate,
            'page_size': ctx.page_size,
            'cur_page': ctx.cur_page,
            'email_search_enabled': not is_email_encrypted,
            'name_op': ctx.name_op,
            'is_name_exact': ctx.is_name_exact,
        }

        # User ID has priority over everything ..
        if ctx.user_id is not not_given:
            config['user_id'] = ctx.user_id

        # .. followed up by username ..
        elif ctx.username is not not_given:
            config['username'] = ctx.username

        # .. and only then goes everything else.
        else:

            for name in SSOSearch.name_columns:
                value = getattr(ctx, name)
                if value is not not_given:
                    name_key = config.setdefault('name', {})
                    name_key[name] = value

            for name in SSOSearch.non_name_column_op:
                value = getattr(ctx, name)
                if value is not not_given:
                    config[name] = value

        with closing(self.odb_session_func()) as session:

            # Output dictionary with all the data found, if any, along with pagination metadata
            out = {
                'total': None,
                'num_pages': None,
                'page_size': None,
                'cur_page': None,
                'has_next_page': None,
                'has_prev_page': None,
                'next_page': None,
                'prev_page': None,
                'result': []
            }

            # Get data from SQL ..
            sql_result = sso_search.search(session, config)

            # .. attach metadata ..
            out['total'] = sql_result.total
            out['num_pages'] = sql_result.num_pages
            out['page_size'] = sql_result.page_size
            out['cur_page'] = sql_result.cur_page
            out['has_next_page'] = sql_result.has_next_page
            out['has_prev_page'] = sql_result.has_prev_page
            out['next_page'] = sql_result.next_page
            out['prev_page'] = sql_result.prev_page

            # .. and append any data found.
            for sql_item in sql_result.result:
                sql_item = sql_item._asdict()

                # Main user entity
                item = UserEntity()

                # Custom attributes
                item.attr = AttrAPI(cid, current_session.user_id, current_session.is_super_user, current_app, remote_addr,
                    self.odb_session_func, self.is_sqlite, self.encrypt_func, self.decrypt_func, sql_item['user_id'])

                # Write out all super-user accessible attributes for each output row
                for name in sorted(_all_super_user_attrs):
                    value = sql_item.get(name)

                    # Serialize datetime objects to string, if needed
                    if serialize_dt and isinstance(value, datetime):
                        value = value.isoformat()

                    # Decrypt email, if needed
                    if name == 'email':
                        if is_email_encrypted:
                            value = self.decrypt_func(value)

                    setattr(item, name, value)

                out['result'].append(item.to_dict())

            return out

# ################################################################################################################################
