# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.cli import ZatoCommand, common_odb_opts, common_totp_opts
from zato.common.util.api import as_bool

# ################################################################################################################################

if 0:

    # stdlib
    from argparse import Namespace

    # Bunch
    from bunch import Bunch

    # Python 2/3 compatibility
    from past.builtins import unicode

    # Zato
    from zato.common.odb.model import SSOUser
    from zato.sso.api import UserAPI

    # For pyflakes
    Bunch = Bunch
    Namespace = Namespace
    SSOUser = SSOUser
    unicode = unicode
    UserAPI = UserAPI

# ################################################################################################################################
# ################################################################################################################################

class SSOCommand(ZatoCommand):
    """ Base class for SSO-related commands.
    """
    user_required = True

# ################################################################################################################################

    def _get_cid(self):
        return 'cli'

# ################################################################################################################################

    def _get_current_app(self):
        return 'zato-cli'

# ################################################################################################################################

    def _get_current_host(self):

        # Zato
        from zato.common.util.api import current_host

        return current_host()

# ################################################################################################################################

    def _get_user(self):

        # Zato
        from zato.common.util.api import current_host, current_user

        return '{}@{}'.format(current_user(), current_host())

# ################################################################################################################################

    def _get_sso_config(self, args, repo_location, secrets_conf):
        # type: (Namespace, unicode, Bunch) -> UserAPI

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

        def _get_session():
            return self.get_odb_session_from_server_config(server_conf, None)

        def _hash_secret(_secret):
            return crypto_manager.hash_secret(_secret, 'sso.super-user')

        user_api = UserAPI(None, sso_conf, None, crypto_manager.encrypt, crypto_manager.decrypt, _hash_secret, None, new_user_id)
        user_api.post_configure(_get_session, True, False)

        return user_api

# ################################################################################################################################

    def execute(self, args):
        # type: (Namespace) -> object

        # stdlib
        import os

        # Zato
        from zato.common.util.api import get_config

        repo_location = os.path.join(args.path, 'config', 'repo')
        secrets_conf = get_config(repo_location, 'secrets.conf', needs_user_config=False)

        # This file must exist, otherwise it's not a path to a server
        if not secrets_conf:
            self.logger.warn('Could not find file `secrets.conf` in `%s`', repo_location)
            return self.SYS_ERROR.NOT_A_ZATO_SERVER

        user_api = self._get_sso_config(args, repo_location, secrets_conf)

        if self.user_required:
            user = user_api.get_user_by_username(self._get_cid(), args.username)
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

    allow_empty_secrets = False
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

        # Bunch
        from bunch import Bunch

        # Zato
        from zato.common.crypto.api import CryptoManager
        from zato.sso import ValidationError

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

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

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

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

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

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

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

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)
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
        {'name': '--must-change', 'help': "A flag indicating whether the password must be changed on next login", 'type':as_bool},
    ]

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

        # Zato
        from zato.sso import ValidationError

        try:
            user_api.set_password(
                self._get_cid(), user.user_id, args.password, args.must_change, args.expiry, self._get_current_app(),
                self._get_current_host())
        except ValidationError as e:
            self.logger.warn('Password validation error, reason code:`%s`', ', '.join(e.sub_status))
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
        {'name': '--must-change', 'help': "A flag indicating whether the password must be changed on next login", 'type':as_bool},
    ]

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

        # Zato
        from zato.common.crypto.api import CryptoManager

        new_password = CryptoManager.generate_password()
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

    def _on_sso_command(self, args, user, user_api):
        # type: (Namespace, SSOUser, UserAPI)

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

    def execute(self, args, show_output=True):
        # type: (Namespace)

        # Zato
        from zato.common.odb.model.sso import \
             _SSOAttr, \
             _SSOFlowPRT, \
             _SSOGroup, \
             _SSOLinkedAuth, \
             _SSOSession, \
             _SSOUser, \
             _SSOUserGroup, \
             Base as SSOModelBase

        _sso_tables = [
            _SSOAttr.__table__,
            _SSOGroup.__table__,
            _SSOFlowPRT.__table__,
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

class GenData(ZatoCommand):
    """ Generates test data for Zato SSO ODB
    """

    opts = [
        {'name': '--super_user_ust', 'help': "Super user's session token", 'required': True},
        {'name': '--n-users', 'help': "Number of users to create", 'required': True, 'type': int},
        {'name': '--mu', 'help': "Maximum number of attributes", 'required': True, 'type': int},
        {'name': '--current-app', 'help': "Name of the application the user is signing up through", 'default': "CRM"},
        {'name': '--save-to-csv', 'help': "Name of the CSV file to create with the generated information"},
        {'name': '--debug', 'help': 'Output sent data', 'action': 'store_true'},
    ]

    def _generate_entry(self, fields=0):
        import random
        from mimesis import Generic
        generic = Generic()

        fixed_fields = [
            'email',
            'occupation',
            'language',
            'height',
            'weight',
            'academic_degree',
            'age',
            'avatar',
            'social_media_profile',
            'telephone',
            'university',
            'work_experience',
        ]

        person = {}
        person['username'] = generic.person.username()
        person['password'] = generic.person.password(length=20, hashed=True)

        number_extra_fields = fields - len(fixed_fields)
        for _ in range(fields - number_extra_fields):
            attr = None
            while attr is None and attr not in person.keys():
                attr = random.choice(fixed_fields)
            get_attr = getattr(generic.person, attr)
            person[attr] = get_attr()

        for _ in range(number_extra_fields):
            field_name = None
            while field_name is None and field_name not in person.keys():
                field_name = generic.text.word()
            person[field_name] = generic.text.sentence()

        return person

    def execute(self, args, show_output=True):
        # type: (Namespace)

        import csv
        import json
        import numpy as np
        import pandas as pd
        import random
        import requests
        from zato.common.crypto.totp_ import TOTPManager

        mu, sigma = 0, 3 # mean and standard deviation

        # generate sequence
        random_nums = np.random.default_rng().normal(mu, sigma, args.n_users)

        # adjusting list's values by rule of three using the max number
        random_ints = np.absolute(np.round(np.multiply(random_nums, int(args.mu)/random_nums.max())))

        list_of_users = []

        for i in random_ints.astype(int).tolist():
            list_of_users.append(self._generate_entry(fields=i))

        try:
            for user in list_of_users:
                self.logger.info('Creating user: {}'.format(user['username']))

                response = requests.post('http://localhost:17010/zato/sso/user/signup', json={
                    'username': user['username'],
                    'password': user['password'],
                    'current_app': args.current_app,
                })
                r = response.json()

                if r['status'] == 'ok' and len(r['sub_status']) == 0:
                    user['confirm_token'] = r['confirm_token']
                    user['confirmed'] = False
                    user['approved'] = False

                    # User Approval
                    if random.choice([True, False]):
                        response = requests.post('http://localhost:17010/zato/sso/user/approve', json={
                            'ust': args.super_user_ust,
                            'confirm_token': user['confirm_token'],
                            'current_app': args.current_app,
                        })
                        r = response.json()

                        if r['status'] == 'ok' and len(r['sub_status']) == 0:
                            self.logger.info('User {} was approved'.format(user['username']))
                            user['approved'] = True
                        else:
                            self.logger.info("Failed to approve user: {}".format(r['sub_status']))

                    if random.choice([True, False]):
                        response = requests.patch('http://localhost:17010/zato/sso/user/signup', json={
                            'confirm_token': user['confirm_token'],
                            'current_app': args.current_app,
                        })
                        r = response.json()

                        if r['status'] == 'ok' and len(r['sub_status']) == 0:
                            self.logger.info("User '{}' was confirmed".format(user['username']))
                            user['confirmed'] = True
                        else:
                            self.logger.info("Failed to confirm user: {}".format(r['sub_status']))

                    self.logger.info("Getting user_id")

                    response = requests.get('http://localhost:17010/zato/sso/user/search', json={
                        'ust': args.super_user_ust,
                        'username': user['username'],
                        'current_app': args.current_app,
                    })
                    r = response.json()

                    if r['status'] == 'ok' and len(r['sub_status']) == 0 and len(r['result']) == 1:
                        user_id = r['result'][0]['user_id']

                        # Add attributes
                        self.logger.info('Adding attributes')
                        requests.post('http://localhost:17010/zato/sso/session/attr', json={
                            'ust': args.super_user_ust,
                            'current_app': args.current_app,
                            'user_id': user_id,
                            'data': [{'user_id': attrib, 'value': user[attrib]} for attrib in user.keys() if attrib not in ['username', 'password', 'confirm_token', 'approved']],
                        })

                        r = response.json()

                        if r['status'] == 'ok':
                            self.logger.info("All attributes were added to user '{}'".format(user['username']))
                        else:
                            self.logger.info("Failed to add attributes to user '{}': {}".format(user['username'], r['sub_status']))
                    else:
                        self.logger.info("Failed to add attributes to user '{}': {}".format(user['username'], r['sub_status']))
                else:
                    self.logger.info("user/signup failed: {}".format(r['sub_status']))
                    break

        except Exception as e:
            self.logger.error(e)
            return self.SYS_ERROR.EXCEPTION_CAUGHT


        if args.save_to_csv != "":
            df = pd.DataFrame(list_of_users)
            df.to_csv(args.save_to_csv, quoting=csv.QUOTE_NONNUMERIC)

        if show_output:
            if self.verbose:
                self.logger.debug('SSO Data inserted successfully')
            else:
                self.logger.info('OK')

# ################################################################################################################################
