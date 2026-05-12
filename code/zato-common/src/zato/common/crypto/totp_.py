# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyOTP
import pyotp
from pyotp.totp import TOTP

# ################################################################################################################################
# ################################################################################################################################

class TOTPManager:

    @staticmethod
    def generate_totp_key() -> 'str':
        return pyotp.random_base32()

    @staticmethod
    def verify_totp_code(totp_key:'str', totp_code:'str') -> 'str':
        return TOTP(totp_key).verify(totp_code)

    @staticmethod
    def get_current_totp_code(totp_key:'str') -> 'str':
        return TOTP(totp_key).now()

# ################################################################################################################################
# ################################################################################################################################
