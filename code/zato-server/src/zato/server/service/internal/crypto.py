# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Integer, Service

# ################################################################################################################################

class Encrypt(Service):
    """ Encrypts data given on input using the server's default key.
    """
    input = 'clear_text'
    output = 'encrypted'

    def handle(self):
        self.response.payload.encrypted = self.crypto.encrypt(self.request.input.clear_text.encode('utf8'))

# ################################################################################################################################

class Decrypt(Service):
    """ Decrypts data previously encrypted using the server's default key.
    """
    input = 'encrypted'
    output = 'clear_text'

    def handle(self):
        self.response.payload.clear_text = self.crypto.decrypt(self.request.input.encrypted)

# ################################################################################################################################

class HashSecret(Service):
    """ Hashes a secret using the server's default key
    """
    input = 'clear_text'
    output = 'hashed'

# ################################################################################################################################

class VerifyHash(Service):
    """ Returns a boolean flag indicating if given input matches the expected hash.
    """
    input = 'given', 'expected'
    output = 'is_valid'

# ################################################################################################################################

class GenerateSecret(Service):
    """ Generates a new secret of input bits strength.
    """
    input = Integer('bits')
    output = 'secret'

# ################################################################################################################################

class GeneratePassword(Service):
    """ Generates a new password of input bits strength.
    """
    input = Integer('bits')
    output = 'password'

# ################################################################################################################################
