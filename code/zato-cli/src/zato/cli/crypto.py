# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# anyjson
import anyjson

# Zato
from zato.cli import ManageCommand, ZatoCommand
from zato.common.crypto import CryptoManager
from zato.common.util import get_config

# ################################################################################################################################

class CreateSecretKey(ZatoCommand):
    """ Creates a new secret key.
    """
    def execute(self, args):
        self.logger.info(CryptoManager.generate_key())

# ################################################################################################################################

class Encrypt(ZatoCommand):
    """ Encrypts secrets using a public key.
    """
    allow_empty_secrets = True
    opts = [{'name':'--secret', 'help':'Secret to encrypt'}]

    def execute(self, args):
        cm = CryptoManager(pub_key_location=os.path.abspath(args.path))
        cm.load_keys()

        self.logger.info('Encrypted value is [{}]'.format(cm.encrypt(args.secret)))

# ################################################################################################################################

class Decrypt(ZatoCommand):
    """ Decrypts secrets using a private key.
    """
    allow_empty_secrets = True
    opts = [{'name':'--secret', 'help':'Secret to decrypt'}]

    def execute(self, args):
        cm = CryptoManager(priv_key_location=os.path.abspath(args.path))
        cm.load_keys()

        self.logger.info('Secret is [{}]'.format(cm.decrypt(args.secret)))

# ################################################################################################################################

class UpdateCrypto(ManageCommand):
    """ Updates cryptographic material of a given Zato component.
    """
    opts = [
        {'name':'pub_key_path', 'help':'Path to a public key in PEM'},
        {'name':'priv_key_path', 'help':'Path to a private key in PEM'},
        {'name':'cert_path', 'help':"Path to a component's certificate in PEM"},
        {'name':'ca_certs_path', 'help':"Path to a bundle of CA certificates in PEM"},
    ]

# ################################################################################################################################

    def _update_crypto(
            self, args, copy_crypto_func, update_secrets=False, load_secrets_func=None,
            store_secrets_func=None, conf_file_name=None, priv_key_name=None, pub_key_name=None, secret_names=[]):

        repo_dir = os.path.join(os.path.abspath(os.path.join(self.original_dir, args.path)), 'config', 'repo')
        secrets = {}

        if update_secrets:
            priv_key_location = os.path.abspath(os.path.join(repo_dir, priv_key_name))
            pub_key_location = os.path.abspath(os.path.join(repo_dir, pub_key_name))
            conf_location = os.path.join(repo_dir, conf_file_name)

            cm = CryptoManager(priv_key_location=priv_key_location)
            cm.load_keys()

            secrets, conf = load_secrets_func(secrets, secret_names, cm, conf_location, conf_file_name)

        copy_crypto_func(repo_dir, args)

        if update_secrets:
            cm.reset()
            cm.pub_key_location = pub_key_location
            cm.load_keys()

            store_secrets_func(secrets, secret_names, cm, conf_location, conf)

# ################################################################################################################################

    def _on_lb(self, args):
        self._update_crypto(args, self.copy_lb_crypto)

# ################################################################################################################################

    def _on_web_admin(self, args):
        def load_secrets(secrets, secret_names, crypto_manager, conf_location, ignored):
            conf = anyjson.loads(open(conf_location).read())
            for name in secret_names:
                secrets[name] = crypto_manager.decrypt(conf[name])

            return secrets, conf

        def store_secrets(secrets, secret_names, crypto_manager, conf_location, conf):
            for name in secret_names:
                conf[name] = crypto_manager.encrypt(secrets[name])
            open(conf_location, 'w').write(anyjson.dumps(conf))

        self._update_crypto(
            args, self.copy_web_admin_crypto, True, load_secrets, store_secrets, 'web-admin.conf',
            'web-admin-priv-key.pem', 'web-admin-pub-key.pem', ['DATABASE_PASSWORD', 'TECH_ACCOUNT_PASSWORD'])

# ################################################################################################################################

    def _on_server(self, args):
        def load_secrets(secrets, secret_names, crypto_manager, conf_location, conf_file_name):
            conf = get_config(os.path.dirname(conf_location), conf_file_name, False)
            for name in secret_names:
                k, v = name.split(':')
                if conf[k][v]:
                    secrets[name] = crypto_manager.decrypt(conf[k][v])

            return secrets, conf

        def store_secrets(secrets, secret_names, crypto_manager, conf_location, conf):
            for name in secret_names:
                if name in secrets:
                    k, v = name.split(':')
                    conf[k][v] = crypto_manager.encrypt(secrets[name])

            conf.filename = conf_location
            conf.write()

        self._update_crypto(
            args, self.copy_server_crypto, True, load_secrets, store_secrets, 'server.conf',
            'zato-server-priv-key.pem', 'zato-server-pub-key.pem', ['odb:password', 'kvdb:password'])

# ################################################################################################################################

class GetHashRounds(ZatoCommand):
    """ Encrypts secrets using a public key.
    """
    allow_empty_secrets = True
    opts = [
        {'name':'--json', 'help':'Output full info in JSON', 'action':'store_true'},
        {'name':'--rounds-only', 'help':'Output only rounds in plain text', 'action':'store_true'},
        {'name':'goal',   'help':'How long a single hash should take in seconds (e.g. 0.2)'},
    ]

# ################################################################################################################################

    def header_func(self, cpu_info, goal):
        self.logger.info('-' * 70)
        self.logger.info('Algorithm ........... PBKDF2-SHA512, salt size 64 bytes (512 bits)')
        self.logger.info('CPU brand ........... {}'.format(cpu_info['brand']))
        self.logger.info('CPU frequency........ {}'.format(cpu_info['hz_actual']))
        self.logger.info('Goal ................ {} sec'.format(goal))
        self.logger.info('-' * 70)

# ################################################################################################################################

    def footer_func(self, rounds_per_second_str, rounds_str):
        self.logger.info('-' * 70)
        self.logger.info('Performance ......... {} rounds/s'.format(rounds_per_second_str))
        self.logger.info('Required for goal ... {} rounds'.format(rounds_str))
        self.logger.info('-' * 70)

# ################################################################################################################################

    def progress_func(self, current_per_cent):
        self.logger.info('Done % .............. {:<3}'.format(100 if current_per_cent >= 100 else current_per_cent))

# ################################################################################################################################

    def execute(self, args):
        goal = round(float(args.goal), 2)

        if args.json or args.rounds_only:
            header_func, progress_func, footer_func = None, None, None
        else:
            header_func, progress_func, footer_func = self.header_func, self.progress_func, self.footer_func

        info = CryptoManager.get_hash_rounds(goal, header_func, progress_func, footer_func)

        if args.json:
            self.logger.info(anyjson.dumps(info))
        elif args.rounds_only:
            self.logger.info(info['rounds'])

# ################################################################################################################################
