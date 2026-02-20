from typing import Any, TYPE_CHECKING

import pyotp
from pyotp.totp import TOTP


class TOTPManager:
    @staticmethod
    def generate_totp_key() -> str: ...
    @staticmethod
    def verify_totp_code(totp_key: str, totp_code: str) -> str: ...
    @staticmethod
    def get_current_totp_code(totp_key: str) -> str: ...
