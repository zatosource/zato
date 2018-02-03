# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import base64
import os
import logging

# Bunch
from bunch import bunchify

# configobj
from configobj import ConfigObj

# cryptography
from cryptography.fernet import Fernet

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

well_known_data = b'3.141592...' # π number

# ################################################################################################################################

class CryptoManager(object):
    """ Used for encryption and decryption of secrets.
    """
    def __init__(self, secrets_conf_path=None, secret_key=None):
        if secrets_conf_path:
            self.secrets_conf = bunchify(ConfigObj(secrets_conf_path, use_zato=False))
            self.secret_key = Fernet(self.secrets_conf.secret_keys.key1)
            self.check_consistency()
        else:
            self.secret_key = Fernet(secret_key.encode('utf8'))

# ################################################################################################################################

    @staticmethod
    def generate_key():
        return Fernet.generate_key()

# ################################################################################################################################

    @staticmethod
    def generate_password(bits=128):
        return base64.urlsafe_b64encode(os.urandom(int(bits / 8)))

# ################################################################################################################################

    def check_consistency(self):
        """ Used as a consistency check to confirm that a given component's key can decrypt well-known data.
        """
        decrypted = self.decrypt(self.secrets_conf.well_known.data)
        if decrypted != well_known_data:
            raise ValueError('Expected for value `{}` to decrypt to `{}`'.format(encrypted, well_known_data))

# ################################################################################################################################

    def encrypt(self, data):
        return self.secret_key.encrypt(data)

# ################################################################################################################################

    def decrypt(self, encrypted):
        return self.secret_key.decrypt(encrypted.encode('utf8'))

# ################################################################################################################################
