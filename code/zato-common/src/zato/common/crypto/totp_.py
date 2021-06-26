# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyOTP
import pyotp
from pyotp.totp import TOTP

# ################################################################################################################################
# ################################################################################################################################

class TOTPManager:

    @staticmethod
    def generate_totp_key():
        return pyotp.random_base32()

    @staticmethod
    def verify_totp_code(totp_key, totp_code):
        return TOTP(totp_key).verify(totp_code)

    @staticmethod
    def get_current_totp_code(totp_key):
        return TOTP(totp_key).now()

# ################################################################################################################################
# ################################################################################################################################
