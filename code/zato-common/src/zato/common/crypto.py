# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from base64 import b64decode, b64encode
from hashlib import sha256

# M2Crypto
from M2Crypto import BIO, RSA

logger = logging.getLogger(__name__)

class CryptoManager(object):
    """ Responsible for management of the server's crypto material.
    """
    def __init__(self, priv_key_location=None, pub_key_location=None, 
                 priv_key=None, pub_key=None):
        
        self.priv_key_location = priv_key_location
        self.pub_key_location = pub_key_location
        
        self.priv_key = priv_key
        self.pub_key = pub_key
        
    def _get_bio(self, key):
        bio = BIO.MemoryBuffer(key)
        bio.close()
        
        return bio

    def load_keys(self):
        if self.priv_key_location:
            self.priv_key = RSA.load_key(self.priv_key_location)
        elif self.priv_key:
            bio = self._get_bio(self.priv_key)
            self.priv_key = RSA.load_key_bio(bio)
            
        if self.pub_key_location:
            self.pub_key = RSA.load_pub_key(self.pub_key_location)
        elif self.pub_key:
            bio = self._get_bio(self.pub_key)
            self.pub_key = RSA.load_pub_key_bio(bio)

    def decrypt(self, data, padding=RSA.pkcs1_padding, hexlified=True):
        """ Decrypts data using the private config key. Padding used defaults
        to PKCS#1. hexlified defaults to True and indicates whether the data
        should be hex-decoded before being decrypted.
        """
        if hexlified:
            data = b64decode(data)

        return self.priv_key.private_decrypt(data, padding).replace('\x00', '')

    def encrypt(self, data, padding=RSA.pkcs1_padding, b64=True):
        """ Encrypts data using the public config key. Padding used defaults
        to PKCS#1. b64 defaults to True and indicates whether the data
        should be BASE64-encoded after being encrypted.
        """
        encrypted = self.pub_key.public_encrypt(data, padding)
        if b64:
            return b64encode(encrypted)

        return encrypted
    
    def sign(self, data):
        """ Signs the SHA256 hash of the data using a private key from the BASE64-encoded value.
        """
        signed = self.priv_key.sign(sha256(data).digest())
        return b64encode(signed)
