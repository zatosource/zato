# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from base64 import b64decode, b64encode
from hashlib import sha256

# PyCrypto
from Crypto.PublicKey import RSA as pycrypto_rsa

# rsa
import rsa

logger = logging.getLogger(__name__)

class CryptoManager(object):
    """ Responsible for management of the server's crypto material.
    """
    def __init__(self, priv_key_location=None, priv_key=None, pub_key_location=None, pub_key=None):
        
        self.priv_key_location = priv_key_location
        self.priv_key = priv_key
        
        self.pub_key_location = pub_key_location
        self.pub_key = pub_key
        
    def _pkcs1_from_pkcs8(self, pkcs8):
        """ Private keys saved by CLI are in PKCS#8 but the rsa module needs PKCS#1.
        Note that PKCS#8 deals with private keys only (https://tools.ietf.org/html/rfc5208).
        """
        key = pycrypto_rsa.importKey(pkcs8)
        return key.exportKey()

    def load_keys(self):
        
        if self.pub_key_location:
            pkcs1 = open(self.pub_key_location).read()
            self.pub_key = rsa.key.PublicKey.load_pkcs1_openssl_pem(pkcs1)
        else:
            if self.priv_key_location:
                pkcs8 = open(self.priv_key_location).read()
                pkcs1 = self._pkcs1_from_pkcs8(pkcs8)
            elif self.priv_key:
                pkcs1 = self._pkcs1_from_pkcs8(self._pkcs1_from_pkcs8(self.priv_key))
                
            self.priv_key = rsa.key.PrivateKey.load_pkcs1(pkcs1)
            self.pub_key = rsa.key.PublicKey(self.priv_key.n, self.priv_key.e)

    def decrypt(self, data, hexlified=True):
        """ Decrypts data using the private config key. Padding used defaults
        to PKCS#1. hexlified defaults to True and indicates whether the data
        should be hex-decoded before being decrypted.
        """
        if hexlified:
            data = b64decode(data)

        return rsa.decrypt(data, self.priv_key)

    def encrypt(self, data, b64=True):
        """ Encrypts data using the public config key. Padding used defaults
        to PKCS#1. b64 defaults to True and indicates whether the data
        should be BASE64-encoded after being encrypted.
        """
        encrypted = rsa.encrypt(data, self.pub_key)
        if b64:
            return b64encode(encrypted)

        return encrypted

    def reset(self):
        """ Sets all the keys to None.
        """
        self.priv_key_location = None
        self.pub_key_location = None
        
        self.priv_key = None
        self.pub_key = None
