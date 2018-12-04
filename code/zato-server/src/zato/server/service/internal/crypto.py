# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Integer, Service

# ################################################################################################################################

class Encrypt(Service):
    """ Encrypts data given on input using the server's default key.
    """
    class SimpleIO:
        input_required = ('clear_text',)
        output_required = ('encrypted',)

# ################################################################################################################################

class Decrypt(Service):
    """ Decrypts data previously encrypted using the server's default key.
    """
    class SimpleIO:
        input_required = ('encrypted',)
        output_required = ('clear_text',)

    def handle(self):
        self.response.payload.clear_text = self.crypto.decrypt(self.request.input.encrypted)

# ################################################################################################################################

class HashSecret(Service):
    """ Hashes a secret using the server's default key
    """
    class SimpleIO:
        input_required = ('clear_text',)
        output_required = ('hashed',)

# ################################################################################################################################

class VerifyHash(Service):
    """ Returns a boolean flag indicating if given input matches the expected hash.
    """
    class SimpleIO:
        input_required = ('given', 'expected')
        output_required = ('is_valid',)

# ################################################################################################################################

class GenerateSecret(Service):
    """ Generates a new secret of input bits strength.
    """
    class SimpleIO:
        input_required = (Integer('bits'),)
        output_required = ('secret',)

# ################################################################################################################################

class GeneratePassword(Service):
    """ Generates a new password of input bits strength.
    """
    class SimpleIO:
        input_required = (Integer('bits'),)
        output_required = ('password',)

# ################################################################################################################################
