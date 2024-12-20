# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger

# Zato
from zato.common.audit import audit_pii
from zato.common.crypto.totp_ import TOTPManager
from zato.sso import InvalidTOTPError, status_code, ValidationError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.odb.model import SSOUser
    from zato.common.typing_ import anydict, callable_
    from zato.sso.api import SSOAPI
    from zato.sso.model import RequestCtx
    SSOUser = SSOUser

# ################################################################################################################################
# ################################################################################################################################

logger           = getLogger('zato')
logger_audit_pii = getLogger('zato_audit_pii')

# ################################################################################################################################
# ################################################################################################################################

class TOTPAPI:
    """ An object through which TOTP tokens can be validated and manipulated.
    """
    def __init__(self, sso_api:'SSOAPI', sso_conf:'anydict', decrypt_func:'callable_') -> 'None':
        self.sso_api = sso_api
        self.sso_conf = sso_conf
        self.decrypt_func = decrypt_func

# ################################################################################################################################

    def _ensure_code_is_valid(
        self,
        req_ctx,     # type: RequestCtx
        *,
        code='',       # type: str
        user_totp_key, # type: str
        ):
        """ Checks whether input TOTP token matches the user TOTP key.
        """

        # This may be potentially encrypted ..
        user_totp_key = self.decrypt_func(user_totp_key)

        # .. finally, verify the code ..
        if TOTPManager.verify_totp_code(user_totp_key, code):
            logger_audit_pii.info('TOTP code accepted; cid `%s`', req_ctx.cid)

        # .. the code was invalid ..
        else:

            # .. this goes to logs ..
            msg = 'Invalid TOTP code; cid `%s`'
            logger.warning(msg, req_ctx.cid)
            logger_audit_pii.warning(msg, req_ctx.cid)

            # .. and this specific exception is raised if the code was invalid,
            # .. note, however, that the status code is a generic one because
            # .. this is what will be likely returned to the user.
            raise InvalidTOTPError(status_code.auth.not_allowed, False)

# ################################################################################################################################

    def _ensure_code_exists(self, req_ctx:'RequestCtx', code:'str') -> 'None':

        # We expect to have a code on input ..
        if not code:

            # This goes to logs ..
            msg = 'Missing TOTP code; cid `%s`'
            logger.warning(msg, req_ctx.cid)
            logger_audit_pii.warning(msg, req_ctx.cid)

            # .. this goes to the user and which status code it is,
            # .. will depend on the configuration found in sso.conf.
            if self.sso_conf.login.get('inform_if_totp_missing', False):
                _code = status_code.auth.totp_missing
                _return_status = True
            else:
                _code = status_code.auth.not_allowed
                _return_status = False

            # Notify the caller that TOTP validation failed
            raise ValidationError(_code, _return_status)

# ################################################################################################################################

    def validate_code_for_user(
        self,
        req_ctx, # type: RequestCtx
        *,
        code, # type: str
        user, # type: SSOUser
        ) -> 'None':
        """ Checks whether input TOTP token is valid for a user object.
        """

        # PII audit comes first
        audit_pii.info(req_ctx.cid, 'totp_api.validate_code_for_user', extra={
            'current_app':req_ctx.current_app,
            'remote_addr':req_ctx.remote_addr,
            'has_code':   bool(code),
            'has_user':   bool(user),
        })

        # Raises an exception if code is missing
        self._ensure_code_exists(req_ctx, code)

        # Raises an exception if the input code is invalid
        self._ensure_code_is_valid(req_ctx, code=code, user_totp_key=user.totp_key)

# ################################################################################################################################

    def validate_code(
        self,
        req_ctx, # type: RequestCtx
        *,
        code, # type: str
        ust='',     # type: str
        username='' # type: str
        ) -> 'None':
        """ Checks whether input TOTP token is valid for a UST or username.
        """

        # PII audit comes first
        audit_pii.info(req_ctx.cid, 'totp_api.validate_code', extra={
            'current_app':  req_ctx.current_app,
            'remote_addr':  req_ctx.remote_addr,
            'has_code':     bool(code),
            'has_ust':      bool(ust),
            'has_username': bool(username),
        })

        # Basic validation ..
        if not (ust or username):
            raise ValueError('Exactly one of ust or username is required on input')

        # .. basic validation continued ..
        if ust and username:
            raise ValueError('Cannot provide both ust and username on input')

        # Raises an exception if code is missing
        self._ensure_code_exists(req_ctx, code)

        #
        # Now, we can look up our the user object needed.
        #

        # If we have a UST, we first need to find the corresponding session,
        # which will point us to the underlying username ..
        if ust:
            # This may be potentially encrypted
            ust = self.decrypt_func(ust)
            session = self.sso_api.user.session.get_session_by_ust(ust, datetime.utcnow())
            username = session.username

        # .. either through an input parameter or via UST, at this point we have a username
        user = self.sso_api.user.get_user_by_username(req_ctx.cid, username) # type: SSOUser

        # Raises an exception if the input code is invalid
        self.validate_code_for_user(req_ctx, code=code, user=user)

# ################################################################################################################################
# ################################################################################################################################
