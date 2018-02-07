# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import base64
import logging
import os
import sys
from json import loads

# Bunch
from bunch import bunchify

# configobj
from configobj import ConfigObj

# cryptography
from cryptography.fernet import Fernet, InvalidToken

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

well_known_data = b'3.141592...' # π number
zato_stdin_prefix = 'zato+stdin:///'

# ################################################################################################################################

class SecretKeyError(Exception):
    pass

# ################################################################################################################################

class CryptoManager(object):
    """ Used for encryption and decryption of secrets.
    """
    def __init__(self, repo_dir=None, secret_key=None, stdin_data=None, well_known_data=None):

        # We always get it on input rather than reading it directly because our caller
        # may want to provide it to subprocesses in which case reading it in this process
        # would consume it and the other process would not be able to access it.
        self.stdin_data = stdin_data

        # In case we have a repository directory on input, look up the secret keys and well known data here ..
        if not secret_key:
            if repo_dir:
                secret_key, well_known_data = self.get_config(repo_dir)

        # .. no matter if given on input or through repo_dir, we can set up crypto keys now.
        self.set_config(secret_key, well_known_data)

# ################################################################################################################################

    def get_config(self, repo_dir):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def _find_secret_key(self, secret_key):
        """ It's possible that what is in config files is not a secret key directly, but information where to find it,
        e.g. in environment variables or stdin. This method looks it up in such cases.
        """
        # Environment variables
        if secret_key.startswith('$'):
            try:
                env_key = secret_key[1:].upper()
                value = os.environ[env_key]
            except KeyError:
                raise SecretKeyError('Environment variable not found `{}`'.format(env_key))

        # Read from stdin
        elif secret_key.startswith(zato_stdin_prefix):
            value = self.stdin_data
            if not value:
                raise SecretKeyError('No data provided on stdin')

        elif not secret_key:
            raise SecretKeyError('Secret key is missing')

        # Use the value as it is
        else:
            value = secret_key

        # Fernet keys always require encoding
        value = value.encode('utf8')

        # Create a transient key just to confirm that what we found was syntactically correct
        try:
            Fernet(value)
        except Exception as e:
            raise SecretKeyError(e.message)
        else:
            return value

# ################################################################################################################################

    def set_config(self, secret_key, well_known_data):
        """ Sets crypto attributes and, to be double sure that they are correct,
        decrypts well known data to itself in order to confirm that keys are valid / expected.
        """
        key = self._find_secret_key(secret_key).encode('utf8')
        self.secret_key = Fernet(key)
        self.well_known_data = well_known_data.encode('utf8') if well_known_data else None

        if self.well_known_data:
            self.check_consistency()

# ################################################################################################################################

    def check_consistency(self):
        """ Used as a consistency check to confirm that a given component's key can decrypt well-known data.
        """
        try:
            decrypted = self.decrypt(self.well_known_data)
        except InvalidToken:
            raise SecretKeyError('Invalid key, could not decrypt well-known data')
        else:
            if decrypted != well_known_data:
                raise SecretKeyError('Expected for `{}` to equal to `{}`'.format(decrypted, well_known_data))

# ################################################################################################################################

    @staticmethod
    def generate_key():
        """ Creates a new random string for Fernet keys.
        """
        return Fernet.generate_key()

# ################################################################################################################################

    @staticmethod
    def generate_password(bits=128):
        """ Generates a string strong enough to be a password (default: 128 bits)
        """
        return base64.urlsafe_b64encode(os.urandom(int(bits / 8)))

# ################################################################################################################################

    @classmethod
    def from_repo_dir(cls, secret_key, repo_dir, stdin_data):
        """ Creates a new CryptoManager instance from a path to configuration file(s).
        """
        return cls(secret_key=secret_key, repo_dir=repo_dir, stdin_data=stdin_data)

# ################################################################################################################################

    @classmethod
    def from_secret_key(cls, secret_key, well_known_data=None, stdin_data=None):
        """ Creates a new CryptoManager instance from an already existing secret key.
        """
        return cls(secret_key=secret_key, well_known_data=well_known_data, stdin_data=stdin_data)

# ################################################################################################################################

    def encrypt(self, data):
        """ Encrypts incoming data, which must be a string.
        """
        return self.secret_key.encrypt(data)

# ################################################################################################################################

    def decrypt(self, encrypted):
        """ Returns input data in a clear-text, decrypted, form.
        """
        decrypted = self.secret_key.decrypt(encrypted.encode('utf8'))
        return decrypted

# ################################################################################################################################

    def get_config_entry(self, entry):
        raise NotImplementedError('May be implemented by subclasses')

# ################################################################################################################################

class WebAdminCryptoManager(CryptoManager):
    """ CryptoManager for web-admin instances.
    """
    def get_config(self, repo_dir):
        conf_path = os.path.join(repo_dir, 'web-admin.conf')
        conf = bunchify(loads(open(conf_path).read()))
        return conf['zato_secret_key'], conf['well_known_data']

# ################################################################################################################################

class SchedulerCryptoManager(CryptoManager):
    """ CryptoManager for schedulers.
    """
    def get_config(self, repo_dir):
        conf_path = os.path.join(repo_dir, 'scheduler.conf')
        conf = bunchify(ConfigObj(conf_path, use_zato=False))
        return conf.secret_keys.key1, conf.crypto.well_known_data

# ################################################################################################################################

class ServerCryptoManager(CryptoManager):
    """ CryptoManager for servers.
    """
    def get_config(self, repo_dir):
        conf_path = os.path.join(repo_dir, 'secrets.conf')
        conf = bunchify(ConfigObj(conf_path, use_zato=False))
        return conf.secret_keys.key1, conf.zato.well_known_data

# ################################################################################################################################
