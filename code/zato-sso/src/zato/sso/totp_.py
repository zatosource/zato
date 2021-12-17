# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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

    def _validate_code(
        self,
        req_ctx,     # type: RequestCtx
        *,
        user_totp_key, # type: str
        code='',       # type: str
        ust='',     # type: str
        username='' # type: str
        ):
        """ Checks whether input TOTP token is valid for a UST or username.
        """

        # Basic validation ..
        if not (ust or username):
            raise ValueError('Exactly one of ust or username is required on input')

        # .. basic validation continued ..
        if ust and username:
            raise ValueError('Cannot provide both ust and username on input')

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

        # .. if we are here, it means that we have a code that we can check
        else:

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
        })

        # Raises an exception if the input code is invalid
        self._validate_code(req_ctx, user_totp_key=user.totp_key, code=code, username=user.username)

# ################################################################################################################################
# ################################################################################################################################
