# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# argon2
from argon2.low_level import Type, hash_secret_raw

# cryptography
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Zato
from zato.common.util.backup.config import (
    aes_key_length,
    aes_nonce_length,
    argon2_memory_cost,
    argon2_parallelism,
    argon2_time_cost,
    kdf_salt_length,
)

# ################################################################################################################################
# ################################################################################################################################

def _derive_key(password:'str', salt:'bytes') -> 'bytes':
    secret = password.encode('utf-8')
    out = hash_secret_raw(
        secret=secret,
        salt=salt,
        time_cost=argon2_time_cost,
        memory_cost=argon2_memory_cost,
        parallelism=argon2_parallelism,
        hash_len=aes_key_length,
        type=Type.ID,
    )
    return out

# ################################################################################################################################

def encrypt_archive(archive_bytes:'bytes', password:'str') -> 'bytes':
    salt = os.urandom(kdf_salt_length)
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(aes_nonce_length)
    ciphertext = aesgcm.encrypt(nonce, archive_bytes, None)
    out = salt + nonce + ciphertext
    return out

# ################################################################################################################################

def decrypt_archive(encrypted_data:'bytes', password:'str') -> 'bytes':
    salt = encrypted_data[:kdf_salt_length]
    nonce = encrypted_data[kdf_salt_length:kdf_salt_length + aes_nonce_length]
    ciphertext = encrypted_data[kdf_salt_length + aes_nonce_length:]
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    out = aesgcm.decrypt(nonce, ciphertext, None)
    return out

# ################################################################################################################################
# ################################################################################################################################
