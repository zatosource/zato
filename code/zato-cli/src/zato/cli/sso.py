# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Bunch
from bunch import Bunch

# Zato
from zato.cli import ManageCommand, ZatoCommand
from zato.common.crypto import CryptoManager
from zato.common.util import get_config
from zato.sso import ValidationError
from zato.sso.util import new_user_id
from zato.sso.user import CreateUserCtx, UserAPI

# ################################################################################################################################

class SSOCommand(ZatoCommand):
    """ Base class for SSO-related commands.
    """
    def _get_sso_config(self, args):
        repo_location = os.path.join(args.path, 'config', 'repo')
        sso_conf = get_config(repo_location, 'sso.conf', needs_user_config=False)
        secrets_conf = get_config(repo_location, 'secrets.conf', needs_user_config=False)

        crypto_manager = CryptoManager.from_secret_key(secrets_conf.secret_keys.key1)
        crypto_manager.add_hash_scheme('sso.super-user', sso_conf.hash_secret.rounds_super_user, sso_conf.hash_secret.salt_size)

        server_conf = get_config(
            repo_location, 'server.conf', needs_user_config=False, crypto_manager=crypto_manager, secrets_conf=secrets_conf)

        def _get_session():
            return self.get_odb_session_from_server_config(server_conf, None)

        def _hash_secret(_secret):
            return crypto_manager.hash_secret(_secret, 'sso.super-user')

        return UserAPI(sso_conf, _get_session, crypto_manager.encrypt, crypto_manager.decrypt, _hash_secret, new_user_id)

# ################################################################################################################################

class CreateSuperUser(SSOCommand):
    """ Creates a new SSO super-user
    """
    allow_empty_secrets = True
    opts = [
        {'name': 'username', 'help': 'Username to use'},
        {'name': '--email', 'help': "Super user's email"},
        {'name': '--display-name', 'help': "Person's display name"},
        {'name': '--first-name', 'help': "Person's first name"},
        {'name': '--middle-name', 'help': "Person's middle name"},
        {'name': '--last-name', 'help': "Person's middle name"},
        {'name': '--password', 'help': 'Password'},
    ]

# ################################################################################################################################

    def execute(self, args):

        user_api = self._get_sso_config(args)

        if user_api.get_user_by_username(args.username):
            self.logger.warn('Error, user already exists `%s`', args.username)
            return self.SYS_ERROR.USER_EXISTS

        try:
            user_api.validate_password(args.password)
        except ValidationError as e:
            self.logger.warn('Password validation error, reason code:`%s`', ', '.join(e.sub_status))
            return self.SYS_ERROR.VALIDATION_ERROR

        data = Bunch()
        data.username = args.username
        data.email = args.email or b''
        data.display_name = args.display_name or b''
        data.first_name = args.first_name or b''
        data.middle_name = args.middle_name or b''
        data.last_name = args.last_name or b''
        data.password = args.password

        ctx = CreateUserCtx()
        ctx.data = data

        user_api.create_super_user(ctx)

        self.logger.info('Created super-user `%s`', data.username)

# ################################################################################################################################

class DeleteUser(ZatoCommand):
    """ Deletes an existing user from SSO (super-user or a regular one).
    """
    opts = [
        {'name': 'username', 'help': 'Username to delete'},
        {'name': '--delete-self', 'help': "Force deletion of user's own account"},
    ]

    def execute(self, args):
        self.logger.info('Deleted user `%s`', args.username)

# ################################################################################################################################

class LockUser(ZatoCommand):
    """ Locks a user account. The person may not log in.
    """
    opts = [
        {'name': 'username', 'help': 'User account to lock'},
    ]

    def execute(self, args):
        self.logger.info('Locked user account `%s`', args.username)

# ################################################################################################################################

class UnlockUser(ZatoCommand):
    """ Unlocks a user account
    """
    opts = [
        {'name': 'username', 'help': 'User account to unlock'},
    ]

    def execute(self, args):
        self.logger.info('Unlocked user account `%s`', args.username)

# ################################################################################################################################

class ChangePassword(ZatoCommand):
    """ Changes password of a user given on input.
    """
    opts = [
        {'name': 'username', 'help': 'User to change the password of'},
    ]

    def execute(self, args):
        self.logger.info('Changed password of user `%s`', args.username)

# ################################################################################################################################
