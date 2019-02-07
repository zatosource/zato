# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from logging import getLogger
from traceback import format_exc

# ipaddress
from ipaddress import ip_address

# Zato
from zato.common.audit import audit_pii
from zato.common.odb.model import SSOSession as SessionModel
from zato.sso import const, status_code, Session as SessionEntity, ValidationError
from zato.sso.attr import AttrAPI
from zato.sso.odb.query import get_session_by_ust, get_user_by_username
from zato.sso.util import check_credentials, check_remote_app_exists, new_user_session_token, set_password, validate_password

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

SessionModelTable = SessionModel.__table__
SessionModelInsert = SessionModelTable.insert
SessionModelUpdate = SessionModelTable.update
SessionModelDelete = SessionModelTable.delete

# ################################################################################################################################

class LoginCtx(object):
    """ A set of data about a login request.
    """
    __slots__ = ('remote_addr', 'user_agent', 'has_remote_addr', 'has_user_agent', 'input')

    def __init__(self, remote_addr, user_agent, has_remote_addr, has_user_agent, input):
        self.remote_addr = [ip_address(remote_addr)]
        self.user_agent = user_agent
        self.has_remote_addr = has_remote_addr
        self.has_user_agent = has_user_agent
        self.input = input

# ################################################################################################################################

class VerifyCtx(object):
    """ Wraps information about a verification request.
    """
    __slots__ = ('ust', 'remote_addr', 'input', 'has_remote_addr', 'has_user_agent')

    def __init__(self, ust, remote_addr, current_app, has_remote_addr=None, has_user_agent=None):
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
    __slots__ = ('username', 'user_id', 'ust', 'creation_time', 'expiration_time')

    def __init__(self):
        self.username = None
        self.user_id = None
        self.ust = None
        self.creation_time = None
        self.expiration_time = None

    def to_dict(self, serialize_dt=True):
        return {
            'username': self.username,
            'user_id': self.user_id,
            'ust': self.ust,
            'creation_time': self.creation_time.isoformat() if serialize_dt else self.creation_time,
            'expiration_time': self.expiration_time.isoformat() if serialize_dt else self.expiration_time,
        }

# ################################################################################################################################

class SessionAPI(object):
    """ Logs a user in or out, provided that all authentication and authorization checks succeed,
    or returns details about already existing sessions.
    """
    def __init__(self, sso_conf, encrypt_func, decrypt_func, hash_func, verify_hash_func):
        self.sso_conf = sso_conf
        self.encrypt_func = encrypt_func
        self.decrypt_func = decrypt_func
        self.hash_func = hash_func
        self.verify_hash_func = verify_hash_func
        self.odb_session_func = None

# ################################################################################################################################

    def set_odb_session_func(self, func):
        self.odb_session_func = func

# ################################################################################################################################

    def _check_credentials(self, ctx, user):
        return check_credentials(self.decrypt_func, self.verify_hash_func, user.password, ctx.input['password'])

# ################################################################################################################################

    def _check_remote_app_exists(self, ctx):
        return check_remote_app_exists(ctx.input['current_app'], self.sso_conf.apps.all, logger)

# ################################################################################################################################

    def _check_login_to_app_allowed(self, ctx):
        if ctx.input['current_app'] not in self.sso_conf.apps.login_allowed:
            if self.sso_conf.apps.inform_if_app_invalid:
                raise ValidationError(status_code.app_list.invalid, True)
            else:
                raise ValidationError(status_code.auth.not_allowed, True)
        else:
            return True

# ################################################################################################################################

    def _check_remote_ip_allowed(self, ctx, user, _invalid=object()):

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
        if user.is_locked:
            if self.sso_conf.login.inform_if_locked:
                raise ValidationError(status_code.auth.locked, True)
        else:
            return True

# ################################################################################################################################

    def _check_signup_status(self, user):
        if user.sign_up_status != const.signup_status.final:
            if self.sso_conf.login.inform_if_not_confirmed:
                raise ValidationError(status_code.auth.invalid_signup_status, True)
        else:
            return True

# ################################################################################################################################

    def _check_is_approved(self, user):
        if not user.approval_status == const.approval_status.approved:
            if self.sso_conf.login.inform_if_not_approved:
                raise ValidationError(status_code.auth.invalid_signup_status, True)
        else:
            return True

# ################################################################################################################################

    def _check_password_expired(self, user, _now=datetime.utcnow):
        if _now() > user.password_expiry:
            if self.sso_conf.password.inform_if_expired:
                raise ValidationError(status_code.password.expired, True)
        else:
            return True

# ################################################################################################################################

    def _check_password_about_to_expire(self, user, _now=datetime.utcnow, _timedelta=timedelta):

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
        if user.password_must_change and not ctx.input.get('new_password'):
            if self.sso_conf.password.inform_if_must_be_changed:
                raise ValidationError(status_code.password.must_send_new, True)
        else:
            return True

# ################################################################################################################################

    def _check_login_metadata_allowed(self, ctx):
        if ctx.has_remote_addr or ctx.has_user_agent:
            if ctx.input['current_app'] not in self.sso_conf.apps.login_metadata_allowed:
                raise ValidationError(status_code.password.must_send_new, False)

        return True

# ################################################################################################################################

    def _run_user_checks(self, ctx, user, check_if_password_expired=True):
        """ Runs a series of checks for incoming request and user.
        """
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

    def login(self, ctx, _ok=status_code.ok, _now=datetime.utcnow, _timedelta=timedelta):
        """ Logs a user in, returning session info on success or raising ValidationError on any error.
        """
        # Look up user and raise exception if not found by username
        with closing(self.odb_session_func()) as session:
            user = get_user_by_username(session, ctx.input['username'])
            if not user:
                raise ValidationError(status_code.auth.not_allowed, False)

            # Check credentials first to make sure that attackers do not learn about any sort
            # of metadata (e.g. is the account locked) if they do not know username and password.
            if not self._check_credentials(ctx, user):
                raise ValidationError(status_code.auth.not_allowed, False)

            # It must be possible to log into the application requested (CRM above)
            self._check_login_to_app_allowed(ctx)

            # Common auth checks
            self._run_user_checks(ctx, user)

            # If applicable, password may not be about to expire (this must be after checking that it has not already).
            # Note that it may return a specific status to return (warning or error)
            _about_status = self._check_password_about_to_expire(user)
            if _about_status is not True:
                if _about_status == status_code.warning:
                    _status_code = status_code.password.w_about_to_exp
                    inform = True
                else:
                    _status_code = status_code.password.e_about_to_exp
                    inform = False

                raise ValidationError(_status_code, inform, _about_status)

            # If password is marked as as requiring a change upon next login but a new one was not sent, reject the request.
            self._check_must_send_new_password(ctx, user)

            # If new password is required, we need to validate and save it before session can be created.
            # Note that at this point we already know that the old password was correct so it is safe to set the new one
            # if it is confirmed to be valid. We also know that there is some new password on input because otherwise
            # the check above would have raised a ValidationError.
            if user.password_must_change:
                try:
                    validate_password(self.sso_conf, ctx.input['new_password'])
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

            session.execute(
                SessionModelInsert().values({
                    'ust': ust,
                    'creation_time': creation_time,
                    'expiration_time': expiration_time,
                    'user_id': user.id,
                    'remote_addr': ', '.join(str(elem) for elem in ctx.remote_addr),
                    'user_agent': ctx.user_agent,
            }))
            session.commit()

            info = SessionInfo()
            info.username = user.username
            info.user_id = user.user_id
            info.ust = self.encrypt_func(ust.encode('utf8'))
            info.creation_time = creation_time
            info.expiration_time = expiration_time

            return info

# ################################################################################################################################

    def _get_session_by_ust(self, session, ust, now):
        """ Low-level implementation of self.get_session_by_ust.
        """
        return get_session_by_ust(session, ust, now)

# ################################################################################################################################

    def get_session_by_ust(self, ust, now):
        """ Returns details of an SSO session by its UST.
        """
        with closing(self.odb_session_func()) as session:
            return self._get_session_by_ust(session, ust, now)

# ################################################################################################################################

    def _get(self, session, ust, current_app, remote_addr, needs_decrypt=True, renew=False, needs_attrs=False,
        check_if_password_expired=True, _now=datetime.utcnow):
        """ Verifies if input user session token is valid and if the user is allowed to access current_app.
        On success, if renew is True, renews the session. Returns all session attributes or True,
        depending on needs_attrs's value.
        """
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
            expiration_time = now + timedelta(minutes=self.sso_conf.session.expiry)
            session.execute(
                SessionModelUpdate().values({
                    'expiration_time': expiration_time,
            }).where(
                SessionModelTable.c.ust==ctx.ust
            ))
            return expiration_time
        else:
            # Indicate success
            return sso_info if needs_attrs else True

# ################################################################################################################################

    def verify(self, cid, target_ust, current_ust, current_app, remote_addr):
        """ Verifies a user session without renewing it.
        """
        # PII audit comes first
        audit_pii.info(cid, 'session.verify', extra={'current_app':current_app, 'remote_addr':remote_addr})

        self.require_super_user(cid, current_ust, current_app, remote_addr)

        try:
            with closing(self.odb_session_func()) as session:
                return self._get(session, target_ust, current_app, remote_addr, renew=False)
        except Exception:
            logger.warn('Could not verify UST, e:`%s`', format_exc())
            return False

# ################################################################################################################################

    def renew(self, cid, ust, current_app, remote_addr):
        """ Renew timelife of a user session, if it is valid, and returns its new expiration time in UTC.
        """
        # PII audit comes first
        audit_pii.info(cid, 'session.renew', extra={'current_app':current_app, 'remote_addr':remote_addr})

        with closing(self.odb_session_func()) as session:
            expiration_time = self._get(session, ust, current_app, remote_addr, renew=True, check_if_password_expired=True)
            session.commit()
            return expiration_time

# ################################################################################################################################

    def get(self, cid, target_ust, current_ust, current_app, remote_addr, check_if_password_expired=True):
        """ Gets details of a session given by its UST on input, without renewing it.
        Must be called by a super-user.
        """
        # PII audit comes first
        audit_pii.info(cid, 'session.get', extra={'current_app':current_app, 'remote_addr':remote_addr})

        # Only super-users are allowed to call us
        current_session = self.require_super_user(cid, current_ust, current_app, remote_addr)

        # This returns all attributes ..
        session = self._get_session(target_ust, current_app, remote_addr, check_if_password_expired)

        # .. and we need to build a session entity with a few selected ones only
        out = SessionEntity()
        out.creation_time = session.creation_time
        out.expiration_time = session.expiration_time
        out.remote_addr = session.remote_addr
        out.user_agent = session.user_agent
        out.attr = AttrAPI(cid, current_session.user_id, current_session.is_super_user,
            current_app, remote_addr, self.odb_session_func, self.encrypt_func, self.decrypt_func, session.user_id, session.ust)

        return out

# ################################################################################################################################

    def _get_session(self, ust, current_app, remote_addr, check_if_password_expired=True):
        """ An internal wrapper around self.get which optionally does not require super-user rights.
        """
        with closing(self.odb_session_func()) as session:
            return self._get(session, ust, current_app, remote_addr, renew=False, needs_attrs=True,
                check_if_password_expired=check_if_password_expired)

# ################################################################################################################################

    def get_current_session(self, cid, current_ust, current_app, remote_addr, needs_super_user):
        """ Returns current session info or raises an exception if it could not be found.
        Optionally, requires that a super-user be owner of current_ust.
        """
        # PII audit comes first
        audit_pii.info(cid, 'session.get_current_session', extra={'current_app':current_app, 'remote_addr':remote_addr})

        # Verify current session's very existence first ..
        current_session = self._get_session(current_ust, current_app, remote_addr)
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
            if self._get(session, ust, current_app, remote_addr, needs_decrypt=False, renew=False):

                # .. and if so, delete the session now.
                session.execute(
                    SessionModelDelete().\
                    where(SessionModelTable.c.ust==ust)
                )
                session.commit()

# ################################################################################################################################
