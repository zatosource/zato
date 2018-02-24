# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta

# ipaddress
from ipaddress import ip_address

# Zato
from zato.sso.api import const, status_code, ValidationError
from zato.common.odb.model import SSOSession as SessionModel
from zato.sso.util import validate_password, new_user_session_token
from zato.sso.odb.query import get_session_by_ust, get_user_by_username

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
    __slots__ = ('ust', 'remote_addr', 'input')

    def __init__(self, ust, remote_addr, current_app):
        self.ust = ust
        self.remote_addr = remote_addr
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
    def __init__(self, sso_conf, encrypt_func, decrypt_func, verify_hash_func):
        self.sso_conf = sso_conf
        self.encrypt_func = encrypt_func
        self.decrypt_func = decrypt_func
        self.verify_hash_func = verify_hash_func
        self.odb_session_func = None

# ################################################################################################################################

    def set_odb_session_func(self, func):
        self.odb_session_func = func

# ################################################################################################################################

    def _check_credentials(self, ctx, user):
        password_decrypted = self.decrypt_func(user.password) # It is decrypted but still hashed
        return self.verify_hash_func(ctx.input['password'], password_decrypted)

# ################################################################################################################################

    def _check_login_to_app_allowed(self, ctx):
        if ctx.input['current_app'] not in self.sso_conf.apps.login_allowed:
            if self.sso_conf.main.inform_if_app_invalid:
                raise ValidationError(status_code.app_list.invalid, False)
        else:
            return True

# ################################################################################################################################

    def _check_remote_ip_allowed(self, ctx, user, _invalid=object()):

        ip_allowed = self.sso_conf.login_list.get(user.username, _invalid)

        # Shortcut in the simplest case
        if ip_allowed == '*':
            return True

        # Do not continue if user is not whitelisted but is required to
        if ip_allowed is _invalid:
            if self.sso_conf.login.reject_if_not_listed:
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

    def _check_user_not_locked(self, user):
        if user.is_locked:
            if self.sso_conf.login.inform_if_locked:
                raise ValidationError(status_code.auth.locked)
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
        if not user.is_approved:
            if self.sso_conf.login.inform_if_not_approved:
                raise ValidationError(status_code.auth.invalid_signup_status, True)
        else:
            return True

# ################################################################################################################################

    def _check_password_expired(self, user, _now=datetime.utcnow):
        if _now() > user.password_expiry:
            if self.sso_conf.password.inform_if_expired:
                raise ValidationError(status_code.password.expired)
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
                raise ValidationError(status_code.password.must_send_new)
        else:
            return True

# ################################################################################################################################

    def _check_login_metadata_allowed(self, ctx):
        if ctx.has_remote_addr or ctx.has_user_agent:
            if ctx.input['current_app'] not in self.sso_conf.apps.login_metadata_allowed:
                raise ValidationError(status_code.password.must_send_new, False)

# ################################################################################################################################

    def _run_user_checks(self, ctx, user):
        """ Runs a series of checks for incoming request and user.
        """
        # If applicable, requests must originate in a white-listed IP address
        self._check_remote_ip_allowed(ctx, user)

        # User must not have been locked out of the auth system
        self._check_user_not_locked(user)

        # If applicable, user must be fully signed up, including account creation's confirmation
        self._check_signup_status(user)

        # If applicable, user must be approved by a super-user
        self._check_is_approved(user)

        # Password must not have expired
        self._check_password_expired(user)

        # Current application must be allowed to send login metadata
        self._check_login_metadata_allowed(ctx)

# ################################################################################################################################

    def login(self, ctx, _ok=status_code.ok, _now=datetime.utcnow, _timedelta=timedelta):
        """ Logs a user in, returning session info on success or raising ValidationError on any error.
        """
        # Look up user and raise exception if not found by username
        with closing(self.odb_session_func()) as session:
            user = get_user_by_username(session, ctx.input['username'])
            if not user:
                raise ValidationError(status_code.auth.no_such_user, False)

            # Check credentials first to make sure that attackers do not learn about any sort
            # of metadata (e.g. is the account locked) if they do not know username and password.
            if not self._check_credentials(ctx, user):
                raise ValidationError(status_code.auth.no_such_user, False)

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
                    zzz # Set new password here

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

    def _renew_verify(self, session, ust, current_app, remote_addr, ust_decrypted=False, renew=False, _now=datetime.utcnow):
        """ Verifies if input user session token is valid and if the user is allowed to access current_app.
        On success, if renew is True, renews the session.
        """
        now = _now()
        ctx = VerifyCtx(ust if ust_decrypted else self.decrypt_func(ust), remote_addr, current_app)

        # Look up user and raise exception if not found by input UST
        sso_info = get_session_by_ust(session, ctx.ust, now)

        # Invalid UST or the session has already expired but in either case
        # we can not access it.
        if not sso_info:
            raise ValidationError(status_code.session.no_such_session, False)

        # Common auth checks
        self._run_user_checks(ctx, sso_info)

        # Everything is validated, we can renew the session, if told to.
        if renew:
            session.execute(
                SessionModelUpdate().values({
                    'expiration_time': now + timedelta(minutes=self.sso_conf.session.expiry),
            }).where(SessionModelTable.c.ust==ctx.ust)
            )

        # Indicate success
        return True

# ################################################################################################################################

    def verify(self, *args):
        """ Verifies a user session.
        """
        with closing(self.odb_session_func()) as session:
            out = self._renew_verify(session, *args, renew=False)
            session.commit()
            return out

# ################################################################################################################################

    def renew(self, *args):
        """ Renew timelife of a user session, if it is valid.
        """
        with closing(self.odb_session_func()) as session:
            out = self._renew_verify(session, *args, renew=True)
            session.commit()
            return out

# ################################################################################################################################

    def logout(self, ust, current_app, remote_addr):
        """ Logs a user out of SSO.
        """
        ust = self.decrypt_func(ust)

        with closing(self.odb_session_func()) as session:

            # Check that the session and user exist ..
            if self._renew_verify(session, ust, current_app, remote_addr, ust_decrypted=True, renew=False):

                # .. and if so, delete the session now.
                session.execute(
                    SessionModelDelete().\
                    where(SessionModelTable.c.ust==ust)
                )
                session.commit()

# ################################################################################################################################
