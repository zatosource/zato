# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Bunch
from bunch import Bunch

# Zato
from zato.cli import ZatoCommand, common_odb_opts, common_totp_opts
from zato.cli.util import get_totp_info_from_args
from zato.common.crypto import CryptoManager
from zato.common.odb.model.sso import _SSOAttr, _SSOSession, _SSOUser, Base as SSOModelBase
from zato.common.util import asbool, get_config, current_host
from zato.sso import ValidationError
from zato.sso.api import UserAPI
from zato.sso.util import new_user_id, normalize_password_reject_list

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # stdlib
    from argparse import Namespace

    # Python 2/3 compatibility
    from past.builtins import unicode

    # Zato
    from zato.common.odb.model import SSOUser

    # For pyflakes
    Namespace = Namespace
    SSOUser = SSOUser
    unicode = unicode

# ################################################################################################################################

_current_app = 'zato-cli'
_current_host = current_host()
_cid = 'cli'

# ################################################################################################################################

_sso_tables = [_SSOAttr.__table__, _SSOSession.__table__, _SSOUser.__table__]

# ################################################################################################################################

class SSOCommand(ZatoCommand):
    """ Base class for SSO-related commands.
    """
    user_required = True

    def _get_sso_config(self, args, repo_location, secrets_conf):
        # type: (Namespace, unicode, Bunch) -> UserAPI
        sso_conf = get_config(repo_location, 'sso.conf', needs_user_config=False)
        normalize_password_reject_list(sso_conf)

        crypto_manager = CryptoManager.from_secret_key(secrets_conf.secret_keys.key1)
        crypto_manager.add_hash_scheme('sso.super-user', sso_conf.hash_secret.rounds, sso_conf.hash_secret.salt_size)

        server_conf = get_config(
            repo_location, 'server.conf', needs_user_config=False, crypto_manager=crypto_manager, secrets_conf=secrets_conf)

        def _get_session():
            return self.get_odb_session_from_server_config(server_conf, None)

        def _hash_secret(_secret):
            return crypto_manager.hash_secret(_secret, 'sso.super-user')

        return UserAPI(None, sso_conf, _get_session, crypto_manager.encrypt, crypto_manager.decrypt, _hash_secret, None,
            new_user_id)

# ################################################################################################################################

    def execute(self, args):
        # type: (Namespace) -> object

        repo_location = os.path.join(args.path, 'config', 'repo')
        secrets_conf = get_config(repo_location, 'secrets.conf', needs_user_config=False)

        # This file must exist, otherwise it's not a path to a server
        if not secrets_conf:
            self.logger.warn('Could not find file `secrets.conf` in `%s`', repo_location)
            return self.SYS_ERROR.NOT_A_ZATO_SERVER

        user_api = self._get_sso_config(args, repo_location, secrets_conf)

        if self.user_required:
            user = user_api.get_user_by_username(_cid, args.username)
            if not user:
                self.logger.warn('No such user `%s`', args.username)
                return self.SYS_ERROR.NO_SUCH_SSO_USER
        else:
            user = None

        return self._on_sso_command(args, user, user_api)

# ################################################################################################################################

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, Bunch) -> object
        raise NotImplementedError('Must be implement by subclasses')

# ################################################################################################################################

class _CreateUser(SSOCommand):
    user_required = False
    create_func = None
    user_type = None

    allow_empty_secrets = True
    opts = [
        {'name': 'username', 'help': 'Username to use'},
        {'name': '--email', 'help': "Person's email"},
        {'name': '--display-name', 'help': "Person's display name"},
        {'name': '--first-name', 'help': "Person's first name"},
        {'name': '--middle-name', 'help': "Person's middle name"},
        {'name': '--last-name', 'help': "Person's middle name"},
        {'name': '--password', 'help': 'Password'},
    ]

# ################################################################################################################################

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

        if user_api.get_user_by_username('', args.username):
            self.logger.warn('User already exists `%s`', args.username)
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
        data.sign_up_confirm_token = 'cli.{}'.format(CryptoManager.generate_secret())
        data.is_rate_limit_active = False
        data.rate_limit_def = None
        data.rate_limit_type = None
        data.rate_limit_check_parent_def = False

        func = getattr(user_api, self.create_func)
        func(_cid, data, require_super_user=False, auto_approve=True)

        self.logger.info('Created %s `%s`', self.user_type, data.username)

# ################################################################################################################################

class CreateUser(_CreateUser):
    """ Creates a new regular SSO user
    """
    create_func = 'create_user'
    user_type = 'user'

# ################################################################################################################################

class CreateSuperUser(_CreateUser):
    """ Creates a new SSO super-user
    """
    create_func = 'create_super_user'
    user_type = 'super-user'

# ################################################################################################################################

class DeleteUser(SSOCommand):
    """ Deletes an existing user from SSO (super-user or a regular one).
    """
    opts = [
        {'name': 'username', 'help': 'Username to delete'},
        {'name': '--yes', 'help': 'Do not prompt for confirmation, assume yes', 'action': 'store_true'},
    ]

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

        if not args.yes:
            template = 'Delete user? `{}`'.format(user.username)
            if not self.get_confirmation(template):
                self.logger.info('User `%s` kept intact', user.username)
                return

        user_api.delete_user_by_username(_cid, args.username, None, _current_app, _current_host, skip_sec=True)
        self.logger.info('Deleted user `%s`', args.username)

# ################################################################################################################################

class LockUser(SSOCommand):
    """ Locks a user account. The person may not log in.
    """
    opts = [
        {'name': 'username', 'help': 'User account to lock'},
    ]

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

        user_api.lock_user_cli(user.user_id)
        self.logger.info('Locked user account `%s`', args.username)

# ################################################################################################################################

class UnlockUser(SSOCommand):
    """ Unlocks a user account
    """
    opts = [
        {'name': 'username', 'help': 'User account to unlock'},
    ]

    def _on_sso_command(self, args, user, user_api):
        user_api.lock_user_cli(user.user_id)
        self.logger.info('Unlocked user account `%s`', args.username)

# ################################################################################################################################

class ChangeUserPassword(SSOCommand):
    """ Changes password of a user given on input. Use reset-user-password if new password should be auto-generated.
    """
    opts = [
        {'name': 'username', 'help': 'User to change the password of'},
        {'name': '--password', 'help': 'New password'},
        {'name': '--expiry', 'help': "Password's expiry in days"},
        {'name': '--must-change', 'help': "A flag indicating whether the password must be changed on next login",  'type':asbool},
    ]

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

        user_api.set_password(_cid, user.user_id, args.password, args.must_change, args.expiry, _current_app, _current_host)
        self.logger.info('Changed password for user `%s`', args.username)

# ################################################################################################################################

class ResetUserPassword(SSOCommand):
    """ Sets a new random for user and returns it on output. Use change-password if new password must be given on input.
    """
    opts = [
        {'name': 'username', 'help': 'User to reset the password of'},
        {'name': '--expiry', 'help': "Password's expiry in hours or days"},
        {'name': '--must-change', 'help': "A flag indicating whether the password must be changed on next login", 'type':asbool},
    ]

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

        new_password = CryptoManager.generate_password()
        user_api.set_password(_cid, user.user_id, new_password, args.must_change, args.expiry, _current_app, _current_host)
        self.logger.info('Password for user `%s` reset to `%s`', args.username, new_password)

# ################################################################################################################################

class ResetTOTPKey(SSOCommand):
    """ Resets a user's TOTP secret key. Returns the key on output if one was not given on input.
    """
    opts = common_totp_opts

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

        key, key_label = get_totp_info_from_args(args)

        user_api.reset_totp_key(_cid, None, user.user_id, key, key_label, _current_app, _current_host, skip_sec=True)

        # Output key only if it was not given on input
        if not args.key:
            self.logger.info('TOTP key for user `%s` reset to `%s`', args.username, key)

# ################################################################################################################################

class CreateODB(ZatoCommand):
    """ Creates a new Zato SSO ODB (Operational Database)
    """
    opts = common_odb_opts

    def execute(self, args, show_output=True):
        # type: (Namespace)

        engine = self._get_engine(args)
        SSOModelBase.metadata.create_all(engine, tables=_sso_tables)

        if show_output:
            if self.verbose:
                self.logger.debug('SSO ODB created successfully')
            else:
                self.logger.info('OK')

# ################################################################################################################################
