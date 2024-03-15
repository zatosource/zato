# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.cli import common_totp_opts, ManageCommand
from zato.common.const import ServiceConst
from zato.common.util.open_ import open_r, open_w

# ################################################################################################################################
# ################################################################################################################################

class _WebAdminAuthCommand(ManageCommand):
    def _prepare(self, args):

        import pymysql
        pymysql.install_as_MySQLdb()

        # stdlib
        import os

        # Zato
        from zato.admin.zato_settings import update_globals
        from zato.common.json_internal import loads

        os.chdir(os.path.abspath(args.path))
        base_dir = os.path.join(self.original_dir, args.path)
        config = loads(open_r(os.path.join(base_dir, '.', 'config/repo/web-admin.conf')).read())
        config['config_dir'] = os.path.abspath(args.path)
        update_globals(config, base_dir)

        os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'
        import django
        django.setup()

    def _ok(self, args):
        # Needed because Django took over our logging config
        self.reset_logger(args, True)
        self.logger.info('OK')

# ################################################################################################################################
# ################################################################################################################################

class CreateUser(_WebAdminAuthCommand):
    """ Creates a new Dashboard user
    """
    opts = [
        {'name': '--username', 'help': 'Username to use'},
        {'name': '--email', 'help': 'e-mail the user uses'},
        {'name': '--password', 'help': "Newly created user's password"},
    ]

    def __init__(self, *args, **kwargs):
        super(CreateUser, self).__init__(*args, **kwargs)
        self.is_interactive = True

    # Class django.contrib.auth.management.commands.createsuperuser.Command needs self.stding and self.stdout
    # so we fake them here.
    class _FakeStdout:
        def __init__(self, logger):
            self.logger = logger

        def write(self, msg):
            self.logger.info(msg.strip())

    class _FakeStdin:
        def isatty(self):
            return True

    def is_password_required(self):
        return not self.is_interactive

    def before_execute(self, args):

        # stdlib
        import sys

        super(CreateUser, self).before_execute(args)
        self._prepare(args)

        username = getattr(args, 'username', None)
        email = getattr(args, 'email', None)

        if username or email:
            if not(username and email):
                self.logger.error('Both --username and --email are required if either is provided')
                sys.exit(self.SYS_ERROR.INVALID_INPUT)
            else:
                from django.core.validators import EmailValidator
                from django.core import exceptions
                self.reset_logger(self.args, True)

                try:
                    validator = EmailValidator()
                    validator(email)
                except exceptions.ValidationError:
                    self.logger.error('Invalid e-mail `%s`', email)
                    sys.exit(self.SYS_ERROR.INVALID_INPUT)
                else:
                    self.is_interactive = False

    def execute(self, args, needs_sys_exit=True):

        # stdlib
        import sys
        from traceback import format_exc

        # Django
        from django.contrib.auth.management.commands.createsuperuser import Command
        self.reset_logger(args, True)

        Command.stdout = CreateUser._FakeStdout(self.logger)
        Command.stdin = CreateUser._FakeStdin()

        options = {
            'verbosity':0,
            'database': None,
            'username':self.args.username,
            'email':self.args.email,
        }

        os.environ['DJANGO_SUPERUSER_PASSWORD'] = self.args.password

        try:
            Command().handle(interactive=self.is_interactive, **options)
        except Exception as e:
            if self.args.verbose:
                suffix = ''
                exc_info = format_exc()
            else:
                suffix = '(use --verbose for more information)'
                exc_info = e

            self.logger.error(f'User could not be created, details: `{exc_info}` {suffix}')

            if needs_sys_exit:
                sys.exit(self.SYS_ERROR.INVALID_INPUT)
            else:
                raise
        else:
            self._ok(args)

# ################################################################################################################################
# ################################################################################################################################

class UpdatePassword(_WebAdminAuthCommand):
    """ Updates a Dashboard user's password
    """
    opts = [
        {'name': 'username', 'help': 'Username to change the password of'},
        {'name': '--password', 'help': 'New password'},
    ]

    def before_execute(self, args):
        super(UpdatePassword, self).before_execute(args)
        self._prepare(args)

    def execute(self, args, called_from_wrapper=False):

        if not called_from_wrapper:
            self._prepare(args)

        from django.contrib.auth.management.commands.changepassword import Command
        self.reset_logger(self.args, True)

        # An optional password tells us if we are to use the Django's command
        # or our own wrapper returning the user-provided password without asking for one.
        if getattr(args, 'password', None):
            class _Command(Command):
                def _get_pass(self, *ignored_args, **ignored_kwargs):
                    return args.password
        else:
            _Command = Command

        _Command().handle(username=args.username, database=None)

        if not called_from_wrapper:
            self._ok(args)

# ################################################################################################################################
# ################################################################################################################################

class ResetTOTPKey(_WebAdminAuthCommand):
    """ Resets a user's TOTP secret key. Returns the key on output unless it was given on input.
    """
    opts = common_totp_opts

    def before_execute(self, args):
        super(ResetTOTPKey, self).before_execute(args)
        self._prepare(args)
        self.reset_logger(args, True)

    def execute(self, args):

        # Zato
        from zato.admin.web.util import set_user_profile_totp_key
        from zato.admin.web.models import User
        from zato.admin.web.util import get_user_profile
        from zato.admin.zato_settings import zato_secret_key
        from zato.cli.util import get_totp_info_from_args
        from zato.common.json_internal import dumps

        # Extract or generate a new TOTP key and label
        key, key_label = get_totp_info_from_args(args)
        self.reset_logger(args, True)

        try:
            user = User.objects.get(username=args.username)
        except User.DoesNotExist:
            self.logger.warning('No such user `%s` found in `%s`', args.username, args.path)
            return

        # Here we know we have the user and key for sure, now we need to get the person's profile
        user_profile = get_user_profile(user, False)

        # Everything is ready, we can reset the key ..
        opaque_attrs = set_user_profile_totp_key(user_profile, zato_secret_key, key, key_label)

        # .. and save the modified profile.
        user_profile.opaque1 = dumps(opaque_attrs)
        user_profile.save()

        # Log the key only if it was not given on input. Otherwise the user is expected to know it already
        # and may perhaps want not to disclose it.
        if self.args.key:
            self.logger.info('OK')
        else:
            self.logger.info(key)

# ################################################################################################################################
# ################################################################################################################################

class SetAdminInvokePassword(_WebAdminAuthCommand):
    """ Resets a web-admin user's password that it uses to connect to servers.
    """
    opts = [
        {'name': '--username', 'help': 'Username to reset the password of', 'default':ServiceConst.API_Admin_Invoke_Username},
        {'name': '--password', 'help': 'Password to set'},
    ]

    def execute(self, args):

        # stdlib
        import os

        # Zato
        from zato.common.crypto.api import WebAdminCryptoManager

        # Python 2/3 compatibility
        from zato.common.py23_.past.builtins import unicode

        # Find directories for config data
        os.chdir(os.path.abspath(args.path))
        base_dir = os.path.join(self.original_dir, args.path)
        repo_dir = os.path.join(base_dir, 'config', 'repo')

        # Read config in
        config_path = os.path.join(repo_dir, 'web-admin.conf')
        config_data = open_r(config_path).read()

        # Encrypted the provided password
        cm = WebAdminCryptoManager(repo_dir=repo_dir)
        encrypted = cm.encrypt(args.password.encode('utf8') if isinstance(args.password, unicode) else args.password)

        # Update the config file in-place so as not to reformat its contents
        new_config = []
        for line in config_data.splitlines():
            if 'ADMIN_INVOKE_PASSWORD' in line:
                encrypted = encrypted.decode('utf8') if not isinstance(encrypted, unicode) else encrypted
                line = '  "ADMIN_INVOKE_PASSWORD": "{}",'.format(encrypted)
            new_config.append(line)

        # Save config with the updated password
        new_config = '\n'.join(new_config)
        open_w(config_path).write(new_config)

# ################################################################################################################################
# ################################################################################################################################
