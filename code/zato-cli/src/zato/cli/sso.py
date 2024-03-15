# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ZatoCommand, common_odb_opts, common_totp_opts
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool

# ################################################################################################################################

if 0:

    from argparse import Namespace
    from bunch import Bunch
    from zato.common.odb.model import SSOUser
    from zato.common.typing_ import any_, intnone
    from zato.sso.api import UserAPI

    Bunch = Bunch
    Namespace = Namespace
    SSOUser = SSOUser
    UserAPI = UserAPI

# ################################################################################################################################
# ################################################################################################################################

class SSOCommand(ZatoCommand):
    """ Base class for SSO-related commands.
    """
    user_required = True

# ################################################################################################################################

    def _get_cid(self) -> 'str':
        return 'cli'

# ################################################################################################################################

    def _get_current_app(self) -> 'str':
        return 'zato-cli'

# ################################################################################################################################

    def _get_current_host(self) -> 'str':

        # Zato
        from zato.common.util.api import current_host

        return current_host()

# ################################################################################################################################

    def _get_user(self) -> 'str':

        # Zato
        from zato.common.util.api import current_host, current_user

        return '{}@{}'.format(current_user(), current_host())

# ################################################################################################################################

    def _get_sso_config(self, args:'Namespace', repo_location:'str', secrets_conf:'Bunch') -> 'UserAPI':

        # Zato
        from zato.common.crypto.api import CryptoManager
        from zato.common.util.api import get_config
        from zato.sso.api import UserAPI
        from zato.sso.util import new_user_id, normalize_password_reject_list

        sso_conf = get_config(repo_location, 'sso.conf', needs_user_config=False)
        normalize_password_reject_list(sso_conf)

        crypto_manager = CryptoManager.from_secret_key(secrets_conf.secret_keys.key1)
        crypto_manager.add_hash_scheme('sso.super-user', sso_conf.hash_secret.rounds, sso_conf.hash_secret.salt_size)

        server_conf = get_config(
            repo_location, 'server.conf', needs_user_config=False, crypto_manager=crypto_manager, secrets_conf=secrets_conf)

        def _get_session() -> 'any_':
            return self.get_odb_session_from_server_config(server_conf, None)

        def _hash_secret(_secret:'any_') -> 'any_':
            return crypto_manager.hash_secret(_secret, 'sso.super-user')

        user_api = UserAPI(
            server=cast_('any_', None),
            sso_conf=sso_conf,
            totp=cast_('any_', None),
            odb_session_func=cast_('any_', None),
            encrypt_func=crypto_manager.encrypt,
            decrypt_func=crypto_manager.decrypt,
            hash_func=_hash_secret,
            verify_hash_func=cast_('any_', None),
            new_user_id_func=new_user_id
            )
        user_api.post_configure(_get_session, True, False)

        return user_api

# ################################################################################################################################

    def execute(self, args:'Namespace') -> 'any_':

        # stdlib
        import os

        # Zato
        from zato.common.util.api import get_config

        # This will exist the process if path does not point to a server
        self.ensure_path_is_a_server(args.path)

        repo_location = os.path.join(args.path, 'config', 'repo')
        secrets_conf = get_config(repo_location, 'secrets.conf', needs_user_config=False)

        user_api = self._get_sso_config(args, repo_location, secrets_conf)

        if self.user_required:
            user = user_api.get_user_by_username(self._get_cid(), args.username)
            if not user:
                self.logger.warning('No such user `%s`', args.username)
                return self.SYS_ERROR.NO_SUCH_SSO_USER
        else:
            user = None

        return self._on_sso_command(args, cast_('any_', user), cast_('any_', user_api))

# ################################################################################################################################

    def _on_sso_command(self, args:'Namespace', user:'SSOUser', user_api:'Bunch') -> 'any_':
        raise NotImplementedError('Must be implement by subclasses')

# ################################################################################################################################

class _CreateUser(SSOCommand):

    user_type:'str'   = ''
    create_func:'str' = ''
    user_required:'bool' = False

    allow_empty_secrets:'bool' = False

    opts = [
        {'name': 'username',       'help': 'Username to use'},
        {'name': '--email',        'help': "Person's email"},
        {'name': '--display-name', 'help': "Person's display name"},
        {'name': '--first-name',   'help': "Person's first name"},
        {'name': '--middle-name',  'help': "Person's middle name"},
        {'name': '--last-name',    'help': "Person's middle name"},
        {'name': '--password',     'help': 'Password'},
    ]

# ################################################################################################################################

    def _on_sso_command(self, args:'Namespace', user:'SSOUser', user_api:'UserAPI') -> 'intnone':

        # Bunch
        from bunch import Bunch

        # Zato
        from zato.common.crypto.api import CryptoManager
        from zato.sso import ValidationError

        if user_api.get_user_by_username('', args.username):
            self.logger.warning('User already exists `%s`', args.username)
            return self.SYS_ERROR.USER_EXISTS

        try:
            user_api.validate_password(args.password)
        except ValidationError as e:
            self.logger.warning('Password validation error, reason code:`%s`', ', '.join(e.sub_status))
            return self.SYS_ERROR.VALIDATION_ERROR

        data = Bunch()
        data.username = args.username
        data.email = args.email or b''
        data.display_name = args.display_name or b''
        data.first_name = args.first_name or b''
        data.middle_name = args.middle_name or b''
        data.last_name = args.last_name or b''
        data.password = args.password
        data.sign_up_confirm_token = 'cli.{}'.format(CryptoManager.generate_secret().decode('utf8'))
        data.is_rate_limit_active = False
        data.rate_limit_def = None
        data.rate_limit_type = None
        data.rate_limit_check_parent_def = False

        func = getattr(user_api, self.create_func)
        func(self._get_cid(), data, require_super_user=False, auto_approve=True)

        self.logger.info('Created %s `%s`', self.user_type, data.username)

# ################################################################################################################################

class CreateUser(_CreateUser):
    """ Creates a new regular SSO user
    """
    user_type = 'user'
    create_func = 'create_user'

# ################################################################################################################################

class CreateSuperUser(_CreateUser):
    """ Creates a new SSO super-user
    """
    user_type = 'super-user'
    create_func = 'create_super_user'

# ################################################################################################################################

class DeleteUser(SSOCommand):
    """ Deletes an existing user from SSO (super-user or a regular one).
    """
    opts = [
        {'name': 'username', 'help': 'Username to delete'},
        {'name': '--yes', 'help': 'Do not prompt for confirmation, assume yes', 'action': 'store_true'},
    ]

    def _on_sso_command(self, args:'Namespace', user:'SSOUser', user_api:'UserAPI') -> 'None':

        if not args.yes:
            template = 'Delete user? `{}`'.format(user.username)
            if not self.get_confirmation(template):
                self.logger.info('User `%s` kept intact', user.username)
                return

        user_api.delete_user_by_username(
            self._get_cid(), args.username, None, self._get_current_app(), self._get_current_host(), skip_sec=True)
        self.logger.info('Deleted user `%s`', args.username)

# ################################################################################################################################

class LockUser(SSOCommand):
    """ Locks a user account. The person may not log in.
    """
    opts = [
        {'name': 'username', 'help': 'User account to lock'},
    ]

    def _on_sso_command(self, args:'Namespace', user:'SSOUser', user_api:'UserAPI') -> 'None':

        user_api.lock_user(
            self._get_cid(), user.user_id, None, self._get_current_app(), self._get_current_host(), False, self._get_user())
        self.logger.info('Locked user account `%s`', args.username)

# ################################################################################################################################

class UnlockUser(SSOCommand):
    """ Unlocks a user account
    """
    opts = [
        {'name': 'username', 'help': 'User account to unlock'},
    ]

    def _on_sso_command(self, args:'Namespace', user:'SSOUser', user_api:'UserAPI') -> 'None':

        user_api.unlock_user(
            self._get_cid(), user.user_id, None, self._get_current_app(), self._get_current_host(), False, self._get_user())
        self.logger.info('Unlocked user account `%s`', args.username)

# ################################################################################################################################

class Login(SSOCommand):
    """ Logs a user in.
    """
    opts = [
        {'name': 'username', 'help': 'User to log in as (no password is required)'},
    ]

    def _on_sso_command(self, args:'Namespace', user:'SSOUser', user_api:'UserAPI') -> 'None':

        # Zato
        from zato.common.util.api import current_host

        response = user_api.login(
            self._get_cid(), args.username, None, None, '127.0.0.1', user_agent='Zato CLI {}'.format(current_host()),
            skip_sec=True)
        self.logger.info('User logged in %s', response.to_dict())

# ################################################################################################################################

class Logout(SSOCommand):
    """ Logs a user out by their UST.
    """
    user_required = False

    opts = [
        {'name': 'ust', 'help': 'User session token to log out by'},
    ]

    def _on_sso_command(self, args:'Namespace', user:'SSOUser', user_api:'UserAPI') -> 'None':
        user_api.logout(self._get_cid(), args.ust, None, '127.0.0.1', skip_sec=True)
        self.logger.info('User logged out by UST')

# ################################################################################################################################

class ChangeUserPassword(SSOCommand):
    """ Changes password of a user given on input. Use reset-user-password if new password should be auto-generated.
    """
    opts = [
        {'name': 'username', 'help': 'User to change the password of'},
        {'name': '--password', 'help': 'New password'},
        {'name': '--expiry', 'help': "Password's expiry in days"},
        {'name': '--must-change', 'help': 'A flag indicating whether the password must be changed on next login', 'type':as_bool},
    ]

    def _on_sso_command(self, args:'Namespace', user:'SSOUser', user_api:'UserAPI') -> 'intnone':

        # Zato
        from zato.sso import ValidationError

        try:
            user_api.set_password(
                self._get_cid(), user.user_id, args.password, args.must_change, args.expiry, self._get_current_app(),
                self._get_current_host())
        except ValidationError as e:
            self.logger.warning('Password validation error, reason code:`%s`', ', '.join(e.sub_status))
            return self.SYS_ERROR.VALIDATION_ERROR
        else:
            self.logger.info('Changed password for user `%s`', args.username)

# ################################################################################################################################

class ResetUserPassword(SSOCommand):
    """ Sets a new random for user and returns it on output. Use change-password if new password must be given on input.
    """
    opts = [
        {'name': 'username', 'help': 'User to reset the password of'},
        {'name': '--expiry', 'help': "Password's expiry in hours or days"},
        {'name': '--must-change', 'help': 'A flag indicating whether the password must be changed on next login', 'type':as_bool},
    ]

    def _on_sso_command(self, args:'Namespace', user:'SSOUser', user_api:'UserAPI') -> 'None':

        # Zato
        from zato.common.crypto.api import CryptoManager

        new_password = CryptoManager.generate_password()

        if isinstance(new_password, bytes):
            new_password = new_password.decode('utf8')

        user_api.set_password(
            self._get_cid(), user.user_id, new_password, args.must_change, args.expiry, self._get_current_app(),
            self._get_current_host())

        self.logger.info('Password for user `%s` reset to `%s`', args.username, new_password)

# ################################################################################################################################

class ResetTOTPKey(SSOCommand):
    """ Resets a user's TOTP secret key. Returns the key on output if one was not given on input.
    """
    opts = common_totp_opts

    def _on_sso_command(self, args:'Namespace', user:'SSOUser', user_api:'UserAPI') -> 'None':

        # Zato
        from zato.cli.util import get_totp_info_from_args

        key, key_label = get_totp_info_from_args(args)
        user_api.reset_totp_key(
            self._get_cid(), None, user.user_id, key, key_label, self._get_current_app(), self._get_current_host(), skip_sec=True)

        # Output key only if it was not given on input
        if not args.key:
            self.logger.info('TOTP key for user `%s` reset to `%s`', args.username, key)

# ################################################################################################################################

class CreateODB(ZatoCommand):
    """ Creates a new Zato SSO ODB (Operational Database)
    """
    opts = common_odb_opts

    def execute(self, args:'Namespace', show_output:'bool'=True):

        # Zato
        from zato.common.odb.model.sso import \
             _SSOAttr, \
             _SSOPasswordReset, \
             _SSOGroup, \
             _SSOLinkedAuth, \
             _SSOSession, \
             _SSOUser, \
             _SSOUserGroup, \
             Base as SSOModelBase

        _sso_tables = [
            _SSOAttr.__table__,
            _SSOGroup.__table__,
            _SSOPasswordReset.__table__,
            _SSOLinkedAuth.__table__,
            _SSOSession.__table__,
            _SSOUser.__table__,
            _SSOUserGroup.__table__,
        ]

        engine = self._get_engine(args)
        SSOModelBase.metadata.create_all(engine, tables=_sso_tables)

        if show_output:
            if self.verbose:
                self.logger.debug('SSO ODB created successfully')
            else:
                self.logger.info('OK')

# ################################################################################################################################
