# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from hashlib import sha256
from json import dumps
from logging import getLogger
from traceback import format_exc
from uuid import uuid4

# ipaddress
from ipaddress import ip_address

# Python 2/3 compatibility
from past.builtins import unicode

# Zato
from zato.common import GENERIC, SEC_DEF_TYPE
from zato.common.audit import audit_pii
from zato.common.odb.model import SSOSession as SessionModel
from zato.common.crypto import CryptoManager
from zato.sso import const, status_code, Session as SessionEntity, ValidationError
from zato.sso.attr import AttrAPI
from zato.sso.odb.query import get_session_by_ext_id, get_session_by_ust, get_session_list_by_user_id, get_user_by_id, \
     get_user_by_username
from zato.sso.util import check_credentials, check_remote_app_exists, new_user_session_token, set_password, validate_password

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # stdlib
    from typing import Callable

    # Bunch
    from bunch import Bunch

    # Zato
    from zato.common.odb.model import SSOUser

    # For pyflakes
    Bunch = Bunch
    Callable = Callable
    SSOUser = SSOUser

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

SessionModelTable = SessionModel.__table__
SessionModelInsert = SessionModelTable.insert
SessionModelUpdate = SessionModelTable.update
SessionModelDelete = SessionModelTable.delete

# ################################################################################################################################

_dummy_password='dummy.{}'.format(uuid4().hex)
_ext_sec_type_supported = SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.JWT

# ################################################################################################################################

class LoginCtx(object):
    """ A set of data about a login request.
    """
    __slots__ = ('remote_addr', 'user_agent', 'has_remote_addr', 'has_user_agent', 'input', 'ext_session_id')

    def __init__(self, remote_addr, user_agent, has_remote_addr, has_user_agent, input, ext_session_id=None):
        # type: (unicode, unicode, bool, bool, dict)
        self.remote_addr = [ip_address(remote_addr)]
        self.user_agent = user_agent
        self.has_remote_addr = has_remote_addr
        self.has_user_agent = has_user_agent
        self.input = input
        self.ext_session_id = ext_session_id

# ################################################################################################################################

class VerifyCtx(object):
    """ Wraps information about a verification request.
    """
    __slots__ = ('ust', 'remote_addr', 'input', 'has_remote_addr', 'has_user_agent')

    def __init__(self, ust, remote_addr, current_app, has_remote_addr=None, has_user_agent=None):
        # type: (unicode, unicode, unicode, bool, bool)
        self.ust = ust
        self.remote_addr = remote_addr
        self.has_remote_addr = has_remote_addr
        self.has_user_agent = has_user_agent
        self.input = {
            'current_app': current_app
        }

# ################################################################################################################################

class SessionInfo(object):
    """ Details about an individual session.
    """
    __slots__ = ('username', 'user_id', 'ust', 'creation_time', 'expiration_time', 'has_w_about_to_exp')

    def __init__(self):
        self.username = None # type: unicode
        self.user_id = None # type: unicode
        self.ust = None # type: unicode
        self.creation_time = None # type: unicode
        self.expiration_time = None # type: unicode
        self.has_w_about_to_exp = None # type: bool

    def to_dict(self, serialize_dt=True):
        # type: (bool) -> dict
        return {
            'username': self.username,
            'user_id': self.user_id,
            'ust': self.ust,
            'creation_time': self.creation_time.isoformat() if serialize_dt else self.creation_time,
            'expiration_time': self.expiration_time.isoformat() if serialize_dt else self.expiration_time,
            'has_w_about_to_exp': self.has_w_about_to_exp
        }

# ################################################################################################################################

class SessionAPI(object):
    """ Logs a user in or out, provided that all authentication and authorization checks succeed,
    or returns details about already existing sessions.
    """
    def __init__(self, sso_conf, encrypt_func, decrypt_func, hash_func, verify_hash_func):
        # type: (dict, Callable, Callable, Callable, Callable)
        self.sso_conf = sso_conf
        self.encrypt_func = encrypt_func
        self.decrypt_func = decrypt_func
        self.hash_func = hash_func
        self.verify_hash_func = verify_hash_func
        self.odb_session_func = None
        self.is_sqlite = None
        self.interaction_max_len = 100

# ################################################################################################################################

    def post_configure(self, func, is_sqlite):
        # type: (Callable, bool)
        self.odb_session_func = func
        self.is_sqlite = is_sqlite

# ################################################################################################################################

    def _check_credentials(self, ctx, user_password):
        # type: (LoginCtx) -> bool
        return check_credentials(self.decrypt_func, self.verify_hash_func, user_password, ctx.input['password'])

# ################################################################################################################################

    def _check_remote_app_exists(self, ctx):
        # type: (LoginCtx) -> bool
        return check_remote_app_exists(ctx.input['current_app'], self.sso_conf.apps.all, logger)

# ################################################################################################################################

    def _check_login_to_app_allowed(self, ctx):
        # type: (LoginCtx) -> bool
        if ctx.input['current_app'] not in self.sso_conf.apps.login_allowed:
            if self.sso_conf.apps.inform_if_app_invalid:
                raise ValidationError(status_code.app_list.invalid, True)
            else:
                raise ValidationError(status_code.auth.not_allowed, True)
        else:
            return True

# ################################################################################################################################

    def _check_remote_ip_allowed(self, ctx, user, _invalid=object()):
        # type: (LoginCtx, SSOUser) -> bool

        ip_allowed = self.sso_conf.user_address_list.get(user.username, _invalid)

        # Shortcut in the simplest case
        if ip_allowed == '*':
            return True

        # Do not continue if user is not whitelisted but is required to
        if ip_allowed is _invalid:
            if self.sso_conf.login.reject_if_not_listed:
                return
            else:
                # We are not to reject users if they are not listed, in other words,
                # we are to accept them even if they are not so we return a success flag.
                return True

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

    def _check_user_not_locked(self, user):
        # type: (SSOUser) -> bool

        if user.is_locked:
            if self.sso_conf.login.inform_if_locked:
                raise ValidationError(status_code.auth.locked, True)
        else:
            return True

# ################################################################################################################################

    def _check_signup_status(self, user):
        # type: (SSOUser) -> bool

        if user.sign_up_status != const.signup_status.final:
            if self.sso_conf.login.inform_if_not_confirmed:
                raise ValidationError(status_code.auth.invalid_signup_status, True)
        else:
            return True

# ################################################################################################################################

    def _check_is_approved(self, user):
        # type: (SSOUser) -> bool

        if not user.approval_status == const.approval_status.approved:
            if self.sso_conf.login.inform_if_not_approved:
                raise ValidationError(status_code.auth.invalid_signup_status, True)
        else:
            return True

# ################################################################################################################################

    def _check_password_expired(self, user, _now=datetime.utcnow):
        # type: (SSOUser, datetime) -> bool

        if _now() > user.password_expiry:
            if self.sso_conf.password.inform_if_expired:
                raise ValidationError(status_code.password.expired, True)
        else:
            return True

# ################################################################################################################################

    def _check_password_about_to_expire(self, user, _now=datetime.utcnow, _timedelta=timedelta):
        # type: (SSOUser, datetime, timedelta) -> object

        # Find time after which the password is considered to be about to expire
        threshold_time = user.password_expiry - _timedelta(days=self.sso_conf.password.about_to_expire_threshold)

        # .. check if current time is already past that threshold ..
        if _now() > threshold_time:

            # .. if it is, we may either return a warning and continue ..
            if self.sso_conf.password.inform_if_about_to_expire:
                return status_code.warning

            # .. or it can considered an error, which rejects the request.
            else:
                return status_code.error

        # No approaching expiry, we may continue
        else:
            return True

# ################################################################################################################################

    def _check_must_send_new_password(self, ctx, user):
        # type: (LoginCtx, SSOUser) -> bool

        if user.password_must_change and not ctx.input.get('new_password'):
            if self.sso_conf.password.inform_if_must_be_changed:
                raise ValidationError(status_code.password.must_send_new, True)
        else:
            return True

# ################################################################################################################################

    def _check_login_metadata_allowed(self, ctx):
        # type: (LoginCtx) -> bool

        if ctx.has_remote_addr or ctx.has_user_agent:
            if ctx.input['current_app'] not in self.sso_conf.apps.login_metadata_allowed:
                raise ValidationError(status_code.metadata.not_allowed, False)

        return True

# ################################################################################################################################

    def _run_user_checks(self, ctx, user, check_if_password_expired=True):
        """ Runs a series of checks for incoming request and user.
        """
        # type: (LoginCtx, SSOUser, bool)

        # Input application must have been previously defined
        if not self._check_remote_app_exists(ctx):
            raise ValidationError(status_code.auth.not_allowed, True)

        # If applicable, requests must originate in a white-listed IP address
        if not self._check_remote_ip_allowed(ctx, user):
            raise ValidationError(status_code.auth.not_allowed, True)

        # User must not have been locked out of the auth system
        if not self._check_user_not_locked(user):
            raise ValidationError(status_code.auth.not_allowed, True)

        # If applicable, user must be fully signed up, including account creation's confirmation
        if not self._check_signup_status(user):
            raise ValidationError(status_code.auth.not_allowed, True)

        # If applicable, user must be approved by a super-user
        if not self._check_is_approved(user):
            raise ValidationError(status_code.auth.not_allowed, True)

        # Password must not have expired, but only if input flag tells us to,
        # it may be possible that a user's password has already expired
        # and that person wants to change it in this very call, in which case
        # we cannot reject it on the basis that it is expired - no one would be able
        # to change expired passwords then.
        if check_if_password_expired:
            if not self._check_password_expired(user):
                raise ValidationError(status_code.auth.not_allowed, True)

        # Current application must be allowed to send login metadata
        if not self._check_login_metadata_allowed(ctx):
            raise ValidationError(status_code.auth.not_allowed, True)

# ################################################################################################################################

    def _format_ext_session_id(self, sec_type, sec_def_id, ext_session_id, _ext_sec_type_supported=_ext_sec_type_supported,
        _bearer=b'Bearer '):
        """ Turns information about a security definition and potential external session ID
        into a format that can be used in SQL.
        """
        # Make sure we let in only allowed security definitions
        if sec_type in _ext_sec_type_supported:

            # This is always required
            _ext_session_id = '{}.{}'.format(sec_type, sec_def_id)

            # JWT tokens need to be included if this is the security type used
            if sec_type == SEC_DEF_TYPE.JWT:

                if isinstance(ext_session_id, unicode):
                    ext_session_id = ext_session_id.encode('utf8')

                ext_session_id = ext_session_id.replace(_bearer, b'')

                _ext_session_id += '.{}'.format(sha256(ext_session_id).hexdigest())

            # Return the reformatted external session ID
            return _ext_session_id

        else:
            raise NotImplementedError('Unrecognized sec_type `{}`'.format(sec_type))

# ################################################################################################################################

    def on_external_auth_succeeded(self, cid, sec_type, sec_def_id, sec_def_username, user_id, ext_session_id, totp_code,
        current_app, remote_addr, user_agent=None, _utcnow=datetime.utcnow,
        ):
        """ Invoked when a user succeeded in authentication via means external to default SSO credentials,
        e.g. through Basic Auth or JWT. Creates an SSO session related to that event or renews an existing one.
        """
        # type: (unicode, Bunch, unicode, unicode, unicode, unicode) -> SessionInfo

        remote_addr = remote_addr if isinstance(remote_addr, unicode) else remote_addr.decode('utf8')

        # PII audit comes first
        audit_pii.info(cid, 'session.on_external_auth_succeeded', extra={
            'current_app':current_app,
            'remote_addr':remote_addr,
            'sec.sec_type': sec_type,
            'sec.id': sec_def_id,
            'sec.username': sec_def_username,
        })

        existing_ust = None # type: unicode
        ext_session_id = self._format_ext_session_id(sec_type, sec_def_id, ext_session_id)

        # Check if there is already a session associated with this external one
        sso_session = self._get_session_by_ext_id(sec_type, sec_def_id, ext_session_id)
        if sso_session:
            existing_ust = sso_session.ust

        # .. if there is, renew it ..
        if existing_ust:
            expiration_time = self.renew(cid, existing_ust, current_app, remote_addr, user_agent, False)
            session_info = SessionInfo()
            session_info.ust = existing_ust
            session_info.expiration_time = expiration_time
            return session_info

        # .. otherwise, create a new one. Note that we get here only if
        else:
            ctx = LoginCtx(remote_addr, user_agent, False, False, {
                'user_id': user_id,
                'current_app': current_app,
                'totp_code': totp_code,
                'sec_type': sec_type,
            }, ext_session_id)
            return self.login(ctx, is_logged_in_ext=True)

# ################################################################################################################################

    def _needs_totp_login_check(self, user, is_logged_in_ext, sec_type, _basic_auth=SEC_DEF_TYPE.BASIC_AUTH):
        """ Returns True TOTP should be checked for user during logging in or False otherwise.
        """
        # type: (User, bool, str, str) -> bool
        # If TOTP is enabled for user then return True unless the user is already
        # logged in externally via Basic Auth in which case it is never required
        # because Basic Auth itself does not have any means to relay current TOTP code
        # (short of adding custom Zato-specific HTTP headers or similar parameters).
        if is_logged_in_ext and sec_type == _basic_auth:
            return False
        else:
            return user.is_totp_enabled

# ################################################################################################################################

    def login(self, ctx, _ok=status_code.ok, _now=datetime.utcnow, _timedelta=timedelta, _dummy_password=_dummy_password,
        is_logged_in_ext=False):
        """ Logs a user in, returning session info on success or raising ValidationError on any error.
        """
        # type: (LoginCtx, unicode, datetime, timedelta, unicode, bool) -> SessionInfo

        # Look up user and raise exception if not found by username
        with closing(self.odb_session_func()) as session:

            if ctx.input.get('username'):
                user = get_user_by_username(session, ctx.input['username']) # type: SSOUser
            else:
                user = get_user_by_id(session, ctx.input['user_id']) # type: SSOUser

            # If the user is already logged in externally, this flag will be True,
            # in which case we do not check the credentials - we already know they are valid
            # because they were checked externally and user_id is the SSO user linked to the
            # already validated external credentials.
            if not is_logged_in_ext:

                # Check credentials first to make sure that attackers do not learn about any sort
                # of metadata (e.g. is the account locked) if they do not know username and password.
                if not self._check_credentials(ctx, user.password if user else _dummy_password):
                    raise ValidationError(status_code.auth.not_allowed, False)

            # Check input TOTP key if two-factor authentication is enabled ..
            if self._needs_totp_login_check(user, is_logged_in_ext, ctx.input.get('sec_type')):
                input_totp_code = ctx.input.get('totp_code')
                if not input_totp_code:
                    logger.warn('Missing TOTP code; user `%s`', user.username)
                    raise ValidationError(status_code.auth.not_allowed, False)
                else:
                    user_totp_key = self.decrypt_func(user.totp_key)
                    if not CryptoManager.verify_totp_code(user_totp_key, input_totp_code):
                        logger.warn('Invalid TOTP code; user `%s`', user.username)
                        raise ValidationError(status_code.auth.not_allowed, False)

            # It must be possible to log into the application requested (CRM above)
            self._check_login_to_app_allowed(ctx)

            # Common auth checks
            self._run_user_checks(ctx, user)

            # We assume that we will not have to warn about an approaching password expiry
            has_w_about_to_exp = False

            # If applicable, password may be about to expire (this must be after checking that it has not already).
            # Note that it may return a specific status to return (warning or error)
            _about_status = self._check_password_about_to_expire(user)
            if _about_status is not True:
                if _about_status == status_code.warning:
                    has_w_about_to_exp = True
                else:
                    raise ValidationError(status_code.password.e_about_to_exp, False, _about_status)

            # If password is marked as requiring a change upon next login but a new one was not sent, reject the request.
            self._check_must_send_new_password(ctx, user)

            # If new password is required, we need to validate and save it before session can be created.
            # Note that at this point we already know that the old password was correct so it is safe to set the new one
            # if it is confirmed to be valid. We also know that there is some new password on input because otherwise
            # the check above would have raised a ValidationError.
            if user.password_must_change:
                try:
                    validate_password(self.sso_conf, ctx.input.get('new_password'))
                except ValidationError as e:
                    if e.return_status:
                        raise ValidationError(e.sub_status, e.return_status, e.status)
                else:
                    set_password(self.odb_session_func, self.encrypt_func, self.hash_func, self.sso_conf, user.user_id,
                            ctx.input['new_password'], False)

            # All validated, we can create a session object now
            creation_time = _now()
            expiration_time = creation_time + timedelta(minutes=self.sso_conf.session.expiry)
            ust = new_user_session_token()

            # Create current interaction details for this session
            session_state_change_list = []
            self.update_session_state_change_list(
                session_state_change_list, ctx.remote_addr, ctx.user_agent, 'login', creation_time)
            opaque = {
                'session_state_change_list': session_state_change_list
            }

            session.execute(
                SessionModelInsert().values({
                    'ust': ust,
                    'creation_time': creation_time,
                    'expiration_time': expiration_time,
                    'user_id': user.id,
                    'auth_type': ctx.input.get('sec_type') or const.auth_type.default,
                    'auth_principal': user.username,
                    'remote_addr': ', '.join(str(elem) for elem in ctx.remote_addr),
                    'user_agent': ctx.user_agent,
                    'ext_session_id': ctx.ext_session_id,
                    GENERIC.ATTR_NAME: dumps(opaque)
            }))
            session.commit()

            info = SessionInfo()
            info.username = user.username
            info.user_id = user.user_id
            info.ust = self.encrypt_func(ust.encode('utf8'))
            info.creation_time = creation_time
            info.expiration_time = expiration_time
            info.has_w_about_to_exp = has_w_about_to_exp

            return info

# ################################################################################################################################

    def _get_session_by_ust(self, session, ust, now):
        """ Low-level implementation of self.get_session_by_ust.
        """
        # type: (object, unicode, datetime) -> object

        return get_session_by_ust(session, ust, now)

# ################################################################################################################################

    def get_session_by_ust(self, ust, now):
        """ Returns details of an SSO session by its UST.
        """
        # type: (unicode, datetime) -> object

        with closing(self.odb_session_func()) as session:
            return self._get_session_by_ust(session, ust, now)

# ################################################################################################################################

    def _get_session_by_ext_id(self, sec_type, sec_def_id, ext_session_id=None, _utcnow=datetime.utcnow):

        with closing(self.odb_session_func()) as session:
            return get_session_by_ext_id(session, ext_session_id, _utcnow())

# ################################################################################################################################

    def get_session_by_ext_id(self, sec_type, sec_def_id, ext_session_id=None):
        ext_session_id = self._format_ext_session_id(sec_type, sec_def_id, ext_session_id)
        result = self._get_session_by_ext_id(sec_type, sec_def_id, ext_session_id)

        if result:

            out = {
                'session_state_change_list': self._extract_session_state_change_list(result)
            }

            for name in 'ust', 'creation_time', 'remote_addr', 'user_agent', 'auth_type':
                out[name] = getattr(result, name)

            return out

# ################################################################################################################################

    def _extract_session_state_change_list(self, session_data, _opaque=GENERIC.ATTR_NAME):
        opaque = getattr(session_data, _opaque) or {}
        return opaque.get('session_state_change_list', [])

# ################################################################################################################################

    def update_session_state_change_list(self, current_state, remote_addr, user_agent, ctx_source, now):
        """ Adds information about a user interaction with SSO, keeping the history
        of such interactions to up to max_len entries.
        """
        # type: (list, unicode, unicode, datetime, int)
        if current_state:
            idx = current_state[-1]['idx']
        else:
            idx = 0

        remote_addr = remote_addr if isinstance(remote_addr, list) else [remote_addr]

        if len(remote_addr) == 1:
            remote_addr = str(remote_addr[0])
        else:
            remote_addr = [str(elem) for elem in remote_addr]

        current_state.append({
            'remote_addr': remote_addr,
            'user_agent': user_agent,
            'timestamp_utc': now.isoformat(),
            'ctx_source': ctx_source,
            'idx': idx + 1
        })

        if len(current_state) > self.interaction_max_len:
            current_state.pop(0)

# ################################################################################################################################

    def _get(self, session, ust, current_app, remote_addr, ctx_source, needs_decrypt=True, renew=False, needs_attrs=False,
        user_agent=None, check_if_password_expired=True, _now=datetime.utcnow, _opaque=GENERIC.ATTR_NAME):
        """ Verifies if input user session token is valid and if the user is allowed to access current_app.
        On success, if renew is True, renews the session. Returns all session attributes or True,
        depending on needs_attrs's value.
        """
        # type: (object, unicode, unicode, bool, bool, bool, bool, datetime, unicode) -> object

        now = _now()
        ctx = VerifyCtx(self.decrypt_func(ust) if needs_decrypt else ust, remote_addr, current_app)

        # Look up user and raise exception if not found by input UST
        sso_info = self._get_session_by_ust(session, ctx.ust, now)

        # Invalid UST or the session has already expired but in either case
        # we can not access it.
        if not sso_info:
            raise ValidationError(status_code.session.no_such_session, False)

        # Common auth checks
        self._run_user_checks(ctx, sso_info, check_if_password_expired)

        # Everything is validated, we can renew the session, if told to.
        if renew:

            # Update current interaction details for this session
            opaque = getattr(sso_info, _opaque) or {}
            session_state_change_list = self._extract_session_state_change_list(sso_info)
            self.update_session_state_change_list(session_state_change_list, remote_addr, user_agent, ctx_source, now)
            opaque['session_state_change_list'] = session_state_change_list

            # Set a new expiration time
            expiration_time = now + timedelta(minutes=self.sso_conf.session.expiry)

            session.execute(
                SessionModelUpdate().values({
                    'expiration_time': expiration_time,
                    GENERIC.ATTR_NAME: dumps(opaque),
            }).where(
                SessionModelTable.c.ust==ctx.ust
            ))
            return expiration_time
        else:
            # Indicate success
            return sso_info if needs_attrs else True

# ################################################################################################################################

    def verify(self, cid, target_ust, current_ust, current_app, remote_addr, user_agent=None):
        """ Verifies a user session without renewing it.
        """
        # PII audit comes first
        audit_pii.info(cid, 'session.verify', extra={'current_app':current_app, 'remote_addr':remote_addr})

        self.require_super_user(cid, current_ust, current_app, remote_addr)

        try:
            with closing(self.odb_session_func()) as session:
                return self._get(session, target_ust, current_app, remote_addr, 'verify', renew=False, user_agent=user_agent)
        except Exception:
            logger.warn('Could not verify UST, e:`%s`', format_exc())
            return False

# ################################################################################################################################

    def renew(self, cid, ust, current_app, remote_addr, user_agent=None, needs_decrypt=True):
        """ Renew timelife of a user session, if it is valid, and returns its new expiration time in UTC.
        """
        # PII audit comes first
        audit_pii.info(cid, 'session.renew', extra={'current_app':current_app, 'remote_addr':remote_addr})

        with closing(self.odb_session_func()) as session:
            expiration_time = self._get(
                session, ust, current_app, remote_addr, 'renew', needs_decrypt=needs_decrypt, renew=True,
                user_agent=user_agent, check_if_password_expired=True)
            session.commit()
            return expiration_time

# ################################################################################################################################

    def get(self, cid, target_ust, current_ust, current_app, remote_addr, user_agent=None, check_if_password_expired=True):
        """ Gets details of a session given by its UST on input, without renewing it.
        Must be called by a super-user.
        """
        # PII audit comes first
        audit_pii.info(cid, 'session.get', extra={'current_app':current_app, 'remote_addr':remote_addr})

        # Only super-users are allowed to call us
        current_session = self.require_super_user(cid, current_ust, current_app, remote_addr)

        # This returns all attributes ..
        session = self._get_session(
            target_ust, current_app, remote_addr, 'get', check_if_password_expired, user_agent=user_agent)

        # .. and we need to build a session entity with a few selected ones only
        out = SessionEntity()
        out.creation_time = session.creation_time
        out.expiration_time = session.expiration_time
        out.remote_addr = session.remote_addr
        out.user_agent = session.user_agent
        out.attr = AttrAPI(cid, current_session.user_id, current_session.is_super_user,
            current_app, remote_addr, self.odb_session_func, self.is_sqlite, self.encrypt_func, self.decrypt_func,
            session.user_id, session.ust)

        return out

# ################################################################################################################################

    def _get_session(self, ust, current_app, remote_addr, ctx_source, check_if_password_expired=True, user_agent=None):
        """ An internal wrapper around self.get which optionally does not require super-user rights.
        """
        with closing(self.odb_session_func()) as session:
            return self._get(session, ust, current_app, remote_addr, ctx_source, renew=False, needs_attrs=True,
                check_if_password_expired=check_if_password_expired, user_agent=user_agent)

# ################################################################################################################################

    def get_current_session(self, cid, current_ust, current_app, remote_addr, needs_super_user):
        """ Returns current session info or raises an exception if it could not be found.
        Optionally, requires that a super-user be owner of current_ust.
        """
        # PII audit comes first
        audit_pii.info(cid, 'session.get_current_session', extra={'current_app':current_app, 'remote_addr':remote_addr})

        # Verify current session's very existence first ..
        current_session = self._get_session(current_ust, current_app, remote_addr, 'get_current_session')
        if not current_session:
            logger.warn('Could not verify session `%s` `%s` `%s` `%s`',
                current_ust, current_app, remote_addr, format_exc())
            raise ValidationError(status_code.auth.not_allowed, True)

        # .. the session exists but it may be still the case that we require a super-user on input.
        if needs_super_user:
            if not current_session.is_super_user:
                logger.warn(
                    'Current UST does not belong to a super-user, cannot continue (session.get_current_session), ' \
                    'current user is `%s` `%s`', current_session.user_id, current_session.username)
                raise ValidationError(status_code.auth.not_allowed, True)

        return current_session

# ################################################################################################################################

    def _get_session_list_by_user_id(self, user_id, now=None):
        with closing(self.odb_session_func()) as session:
            result = get_session_list_by_user_id(session, user_id, now or datetime.utcnow())

        for item in result:
            item.pop(GENERIC.ATTR_NAME, None)
        return result

# ################################################################################################################################

    def _get_session_list_by_ust(self, ust):
        now = datetime.utcnow()
        session = self.get_session_by_ust(ust, now)
        return self._get_session_list_by_user_id(session.user_id, now)

# ################################################################################################################################

    def get_list(self, cid, ust, target_ust, current_ust, current_app, remote_addr, _unused_user_agent=None):
        """ Returns a list of sessions. Regular users may receive basic information about their own sessions only
        whereas super-users may look up any other user's session list.
        """
        # PII audit comes first
        audit_pii.info(cid, 'session.get_list', extra={'current_app':current_app, 'remote_addr':remote_addr})

        # Local aliases
        has_ust = bool(ust)
        current_ust_elem = ust if has_ust else current_ust

        current_session = self.get_current_session(cid, current_ust_elem, current_app, remote_addr, False)

        # We return a list of sessions for currently logged in user
        if has_ust:
            return self._get_session_list_by_user_id(current_session.user_id)

        else:
            # If we are to return a list of sessions for another UST, we need to be a super-user
            if not current_session.is_super_user:
                logger.warn(
                    'Current UST does not belong to a super-user, cannot continue (session.get_list), current user is ' \
                    '`%s` `%s`', current_session.user_id, current_session.username)
                raise ValidationError(status_code.auth.not_allowed, True)

            # If we are here, it means that we are a super-user and we are to return sessions
            # by another person's UST but there is still a chance that this other person is actually us.
            if current_ust == target_ust:
                return self._get_session_list_by_user_id(current_session.user_id)
            else:
                return self._get_session_list_by_ust(target_ust)

# ################################################################################################################################

    def require_super_user(self, cid, current_ust, current_app, remote_addr):
        """ Makes sure that current_ust belongs to a super-user or raises an exception if it does not.
        """
        # PII audit comes first
        audit_pii.info(cid, 'session.require_super_user', extra={'current_app':current_app, 'remote_addr':remote_addr})

        return self.get_current_session(cid, current_ust, current_app, remote_addr, True)

# ################################################################################################################################

    def logout(self, ust, current_app, remote_addr):
        """ Logs a user out of an SSO session.
        """
        ust = self.decrypt_func(ust)

        with closing(self.odb_session_func()) as session:

            # Check that the session and user exist ..
            if self._get(session, ust, current_app, remote_addr, 'logout', needs_decrypt=False, renew=False):

                # .. and if so, delete the session now.
                session.execute(
                    SessionModelDelete().\
                    where(SessionModelTable.c.ust==ust)
                )
                session.commit()

# ################################################################################################################################
