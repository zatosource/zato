# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.sso import const, status_code, ValidationError
from zato.sso.password_reset import PasswordResetAPI
from zato.sso.user import Forbidden, User, UserAPI
from zato.sso.totp_ import TOTPAPI

# For flake8
const = const
Forbidden = Forbidden
status_code = status_code
User = User
ValidationError = ValidationError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import callable_, callnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class SSOAPI:
    """ An object through which user management and SSO-related functionality is accessed.
    """
    server:   'ParallelServer'
    sso_conf: 'Bunch'
    odb_session_func: 'callable_'
    encrypt_func:     'callable_'
    decrypt_func:     'callable_'
    hash_func:        'callable_'
    verify_hash_func: 'callable_'
    new_user_id_func: 'callnone' = None

    encrypt_email:    'bool'
    encrypt_password: 'bool'
    password_expiry:  'int'

    totp: 'TOTPAPI'
    user: 'UserAPI'
    password_reset: 'PasswordResetAPI'

    def __init__(
        self,
        server,   # type: ParallelServer
        sso_conf, # type: Bunch
        odb_session_func, # type: callable_
        encrypt_func,     # type: callable_
        decrypt_func,     # type: callable_
        hash_func,        # type: callable_
        verify_hash_func, # type: callable_
        new_user_id_func=None # type: callnone
    ) -> 'None':

        self.server = server
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

        # Management of TOTP tokens
        self.totp = TOTPAPI(self, self.sso_conf, self.decrypt_func)

        # User management, including passwords
        self.user = UserAPI(server, sso_conf, self.totp, odb_session_func, encrypt_func, decrypt_func,
            hash_func, verify_hash_func, new_user_id_func)

        # Management of Password reset tokens (PRT)
        self.password_reset = PasswordResetAPI(server, sso_conf, odb_session_func, decrypt_func, verify_hash_func)

# ################################################################################################################################

    def post_configure(self, func:'callable_', is_sqlite:'bool') -> 'None':
        self.odb_session_func = func
        self.user.post_configure(func, is_sqlite)
        self.password_reset.post_configure(func, is_sqlite)

# ################################################################################################################################
# ################################################################################################################################
