# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import secrets
import threading

# ################################################################################################################################
# ################################################################################################################################

class NUID:
    """ Fast unique identifier generator, compatible with NATS NUIDs.
    """
    DIGITS = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    BASE = 62
    PREFIX_LENGTH = 12
    SEQ_LENGTH = 10
    MAX_SEQ = 839299365868340224

    def __init__(self) -> None:
        self._seq = secrets.randbelow(self.MAX_SEQ)
        self._inc = 33 + secrets.randbelow(300)
        self._prefix = self._random_prefix()
        self._lock = threading.Lock()

    def _random_prefix(self) -> bytearray:
        random_bytes = secrets.token_bytes(self.PREFIX_LENGTH)
        return bytearray(self.DIGITS[b % self.BASE] for b in random_bytes)

    def next(self) -> bytearray:
        with self._lock:
            self._seq += self._inc
            if self._seq >= self.MAX_SEQ:
                self._prefix = self._random_prefix()
                self._seq = secrets.randbelow(self.MAX_SEQ)
                self._inc = 33 + secrets.randbelow(300)

            seq = self._seq
            prefix = self._prefix[:]
            suffix = bytearray(self.SEQ_LENGTH)
            for i in range(self.SEQ_LENGTH - 1, -1, -1):
                suffix[i] = self.DIGITS[seq % self.BASE]
                seq //= self.BASE

            prefix.extend(suffix)
            return prefix

# ################################################################################################################################
# ################################################################################################################################
