# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ManageCommand, ZatoCommand
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

class CreateSecretKey(ZatoCommand):
    """ Creates a new secret key.
    """
    def execute(self, args):

        # Zato
        from zato.common.crypto.api import CryptoManager

        self.logger.info(CryptoManager.generate_key().decode('utf8'))

# ################################################################################################################################
# ################################################################################################################################

class Encrypt(ManageCommand):
    """ Encrypts secrets using a secret key.
    """
    allow_empty_secrets = False
    opts = [
        {'name':'--data', 'help':'Data to encrypt'},
        {'name':'--secret-key', 'help':'Secret key to encrypt data with'},
        {'name':'--path', 'help':'Path to a Zato component where the secret key can be found'},
    ]

# ################################################################################################################################

    def execute(self, args):

        # We need to know what to encrypt
        if not args.data:
            raise ValueError('Parameter --data is required')

        # We are encrypting using a given component's secret key ..
        if args.path:
            super().execute(args)

        # .. otherwise, we use the key we were given on input
        else:
            cm = CryptoManager(secret_key=args.secret_key)
            out = cm.encrypt(args.data)
            out = out.decode('utf8')
            self.logger.info(out)

# ################################################################################################################################

    def _on_web_admin(self, args):

        # Zato
        from zato.common.crypto.api import WebAdminCryptoManager

        self._encrypt(WebAdminCryptoManager, args)

# ################################################################################################################################

    def _on_server(self, args):

        # Zato
        from zato.common.crypto.api import ServerCryptoManager

        self._encrypt(ServerCryptoManager, args)

# ################################################################################################################################

    def _on_scheduler(self, args):

        # Zato
        from zato.common.crypto.api import SchedulerCryptoManager

        self._encrypt(SchedulerCryptoManager, args)

# ################################################################################################################################
# ################################################################################################################################

class Decrypt(ManageCommand):
    """ Decrypts secrets using a secret key.
    """
    allow_empty_secrets = False
    opts = [
        {'name':'--data', 'help':'Data to encrypt'},
        {'name':'--secret-key', 'help':'Secret key to encrypt data with'},
        {'name':'--path', 'help':'Path to a Zato component where the secret key can be found'},
    ]

# ################################################################################################################################

    def execute(self, args):

        # We need to know what to decrypt
        if not args.data:
            raise ValueError('Parameter --data is required')

        # We are decrypting using a given component's secret key ..
        if args.path:
            super().execute(args)

        # .. otherwise, we use the key we were given on input
        else:
            cm = CryptoManager(secret_key=args.secret_key or '')
            out = cm.decrypt(args.data)
            self.logger.info(out)

# ################################################################################################################################

    def _decrypt(self, class_, args):

        # stdlib
        import os

        os.chdir(self.original_dir)
        repo_dir = os.path.abspath(os.path.join(args.path, 'config', 'repo'))
        cm = class_(repo_dir=repo_dir)
        decrypted = cm.decrypt(args.secret)
        self.logger.info(decrypted)

# ################################################################################################################################

    def _on_web_admin(self, args):

        # Zato
        from zato.common.crypto.api import WebAdminCryptoManager

        self._decrypt(WebAdminCryptoManager, args)

# ################################################################################################################################

    def _on_server(self, args):

        # Zato
        from zato.common.crypto.api import ServerCryptoManager

        self._decrypt(ServerCryptoManager, args)

# ################################################################################################################################

    def _on_scheduler(self, args):

        # Zato
        from zato.common.crypto.api import SchedulerCryptoManager

        self._decrypt(SchedulerCryptoManager, args)

# ################################################################################################################################
# ################################################################################################################################

class GetHashRounds(ZatoCommand):
    """ Computes PBKDF2-SHA512 hash rounds.
    """
    opts = [
        {'name':'--json', 'help':'Output full info in JSON', 'action':'store_true'},
        {'name':'--rounds-only', 'help':'Output only rounds in plain text', 'action':'store_true'},
        {'name':'goal',   'help':'How long a single hash should take in seconds (e.g. 0.2)'},
    ]

# ################################################################################################################################

    def allow_empty_secrets(self):
        return True

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

        # Zato
        from zato.common.crypto.api import CryptoManager
        from zato.common.json_internal import dumps

        goal = round(float(args.goal), 2)

        if args.json or args.rounds_only:
            header_func, progress_func, footer_func = None, None, None
        else:
            header_func, progress_func, footer_func = self.header_func, self.progress_func, self.footer_func

        info = CryptoManager.get_hash_rounds(goal, header_func, progress_func, footer_func)

        if args.json:
            self.logger.info(dumps(info))
        elif args.rounds_only:
            self.logger.info(info['rounds'])

# ################################################################################################################################
# ################################################################################################################################
