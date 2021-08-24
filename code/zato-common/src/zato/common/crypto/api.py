# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import base64
import logging
import os
from datetime import datetime
from math import ceil

# Bunch
from bunch import bunchify

# cryptography
from cryptography.fernet import Fernet, InvalidToken

# Python 2/3 compatibility
from builtins import bytes

# Zato
from zato.common.crypto.const import well_known_data, zato_stdin_prefix
from zato.common.ext.configobj_ import ConfigObj
from zato.common.json_internal import loads

# ################################################################################################################################

logger = logging.getLogger(__name__)

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

        # Callers will be able to register their hashing scheme which will end up in this dict by name
        self.hash_scheme = {}

# ################################################################################################################################

    def add_hash_scheme(self, name, rounds, salt_size):
        """ Adds a new named PBKDF2 hashing scheme, i.e. a set of named variables and a hashing object.
        """

        # hashlib
        from passlib import hash as passlib_hash

        self.hash_scheme[name] = passlib_hash.pbkdf2_sha512.using(rounds=rounds, salt_size=salt_size)

# ################################################################################################################################

    def get_config(self, repo_dir):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def _find_secret_key(self, secret_key):
        """ It's possible that what is in config files is not a secret key directly, but information where to find it,
        e.g. in environment variables or stdin. This method looks it up in such cases.
        """
        secret_key = secret_key.decode('utf8') if isinstance(secret_key, bytes) else secret_key

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
        value = value if isinstance(value, bytes) else value.encode('utf8')

        # Create a transient key just to confirm that what we found was syntactically correct.
        # Note that we use our own invalid backend which will not be used by Fernet for anything
        # but we need to provide it to make sure Fernet.__init__ does not import its default backend.
        try:
            Fernet(value, backend='invalid')
        except Exception as e:
            raise SecretKeyError(e.args)
        else:
            return value

# ################################################################################################################################

    def set_config(self, secret_key, well_known_data):
        """ Sets crypto attributes and, to be double sure that they are correct,
        decrypts well known data to itself in order to confirm that keys are valid / expected.
        """
        key = self._find_secret_key(secret_key)
        self.secret_key = Fernet(key)
        self.well_known_data = well_known_data if well_known_data else None

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
    def generate_secret(bits=256):
        """ Generates a secret string of bits size.
        """
        return base64.urlsafe_b64encode(os.urandom(int(bits / 8)))

# ################################################################################################################################

    @staticmethod
    def generate_password(bits=192, to_str=False):
        """ Generates a string strong enough to be a password (default: 192 bits)
        """
        # type: (int, bool) -> str
        value = CryptoManager.generate_secret(bits)
        return value.decode('utf8') if to_str else value

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
        if not isinstance(data, bytes):
            data = data.encode('utf8')
        return self.secret_key.encrypt(data)

# ################################################################################################################################

    def decrypt(self, encrypted):
        """ Returns input data in a clear-text, decrypted, form.
        """
        if not isinstance(encrypted, bytes):
            encrypted = encrypted.encode('utf8')

        return self.secret_key.decrypt(encrypted).decode('utf8')

# ################################################################################################################################

    def hash_secret(self, data, name='zato.default'):
        """ Hashes input secret using a named configured (e.g. PBKDF2-SHA512, 100k rounds, salt 32 bytes).
        """
        return self.hash_scheme[name].hash(data)

# ################################################################################################################################

    def verify_hash(self, given, expected, name='zato.default'):
        return self.hash_scheme[name].verify(given, expected)

# ################################################################################################################################

    @staticmethod
    def get_hash_rounds(goal, header_func=None, progress_func=None, footer_func=None):
        return HashParamsComputer(goal, header_func, progress_func, footer_func).get_info()

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

class HashParamsComputer(object):
    """ Computes parameters for hashing purposes, e.g. number of rounds in PBKDF2.
    """
    def __init__(self, goal, header_func=None, progress_func=None, footer_func=None, scheme='pbkdf2_sha512', loops=10,
            iters_per_loop=10, salt_size=64, rounds_per_iter=25000):

        # hashlib
        from passlib import hash as passlib_hash

        self.goal = goal
        self.header_func = header_func
        self.progress_func = progress_func
        self.footer_func = footer_func
        self.scheme = scheme
        self.loops = loops
        self.iters_per_loop = iters_per_loop
        self.iters = self.loops * self.iters_per_loop
        self.salt_size = salt_size
        self.rounds_per_iter = rounds_per_iter
        self.report_per_cent = 5.0
        self.report_once_in = self.iters * self.report_per_cent / 100.0
        self.hash_scheme = getattr(passlib_hash, scheme).using(salt_size=salt_size, rounds=rounds_per_iter)
        self.cpu_info = self.get_cpu_info()
        self._round_down_to_nearest = 1000
        self._round_up_to_nearest = 5000

# ################################################################################################################################

    def get_cpu_info(self):
        """ Returns metadata about current CPU the computation is executed on.
        """

        # py-cpuinfo
        from cpuinfo import get_cpu_info

        cpu_info = get_cpu_info()
        return {
            'brand': cpu_info['brand'],
            'hz_actual': cpu_info['hz_actual']
        }

# ################################################################################################################################

    def get_info(self, _utcnow=datetime.utcnow):

        if self.header_func:
            self.header_func(self.cpu_info, self.goal)

        all_results = []
        current_iter = 0
        current_loop = 0

        # We have several iterations to take into account sudden and unexpected CPU usage spikes,
        # outliers stemming from such cases which will be rejected.
        while current_loop < self.loops:
            current_loop += 1
            current_loop_iter = 0
            current_loop_result = []

            while current_loop_iter < self.iters_per_loop:
                current_iter += 1
                current_loop_iter += 1

                start = _utcnow()
                self.hash_scheme.hash(well_known_data)
                current_loop_result.append((_utcnow() - start).total_seconds())

                if self.progress_func:
                    if current_iter % self.report_once_in == 0:
                        per_cent = int((current_iter / self.iters) * 100)
                        self.progress_func(per_cent)

            all_results.append(sum(current_loop_result) / len(current_loop_result))

        # On average, that many seconds were needed to create a hash with self.rounds rounds ..
        sec_needed = min(all_results)

        # .. we now need to extrapolate it to get the desired self.goal seconds.
        rounds_per_second = int(self.rounds_per_iter / sec_needed)
        rounds_per_second = self.round_down(rounds_per_second)

        rounds = int(rounds_per_second * self.goal)
        rounds = self.round_up(rounds)

        rounds_per_second_str = '{:,d}'.format(rounds_per_second)
        rounds_str = '{:,d}'.format(rounds).rjust(len(rounds_per_second_str))

        if self.footer_func:
            self.footer_func(rounds_per_second_str, rounds_str)

        return {
            'rounds_per_second': int(rounds_per_second),
            'rounds_per_second_str': rounds_per_second_str.strip(),
            'rounds': int(rounds),
            'rounds_str': rounds_str.strip(),
            'cpu_info': self.cpu_info,
            'algorithm': 'PBKDF2-SHA512',
            'salt_size': self.salt_size,
        }

# ################################################################################################################################

    def round_down(self, value):
        return int(round(value / self._round_down_to_nearest) * self._round_down_to_nearest)

# ################################################################################################################################

    def round_up(self, value):
        return int(ceil(value / self._round_up_to_nearest) * self._round_up_to_nearest)

# ################################################################################################################################
