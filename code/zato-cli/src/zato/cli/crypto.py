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
from zato.common.crypto import CryptoManager, SchedulerCryptoManager, ServerCryptoManager, WebAdminCryptoManager

# ################################################################################################################################

class CreateSecretKey(ZatoCommand):
    """ Creates a new secret key.
    """
    def execute(self, args):
        self.logger.info(CryptoManager.generate_key())

# ################################################################################################################################

class Encrypt(ManageCommand):
    """ Encrypts secrets using a public key.
    """
    allow_empty_secrets = True
    opts = [{'name':'--secret', 'help':'Secret to encrypt'}]

    def _encrypt(self, class_, args):
        repo_dir = os.path.abspath(os.path.join(args.path, 'config', 'repo'))
        cm = class_(repo_dir=repo_dir)
        self.logger.info('Encrypted value: `%s`' % cm.encrypt(args.secret))

    def _on_web_admin(self, args):
        self._encrypt(WebAdminCryptoManager, args)

    def _on_server(self, args):
        self._encrypt(ServerCryptoManager, args)

    def _on_scheduler(self, args):
        self._encrypt(SchedulerCryptoManager, args)

# ################################################################################################################################

class Decrypt(ManageCommand):
    """ Decrypts secrets using a private key.
    """
    allow_empty_secrets = True
    opts = [{'name':'--secret', 'help':'Secret to decrypt'}]

    def _decrypt(self, class_, args):
        repo_dir = os.path.abspath(os.path.join(args.path, 'config', 'repo'))
        cm = class_(repo_dir=repo_dir)
        self.logger.info('Decrypted value: `%s`' % cm.decrypt(args.secret))

    def _on_web_admin(self, args):
        self._decrypt(WebAdminCryptoManager, args)

    def _on_server(self, args):
        self._decrypt(ServerCryptoManager, args)

    def _on_scheduler(self, args):
        self._decrypt(SchedulerCryptoManager, args)

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
