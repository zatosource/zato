# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import json, os, sys
from traceback import format_exc

# Zato
from zato.admin.zato_settings import update_globals
from zato.cli import ManageCommand

# ################################################################################################################################

class _WebAdminAuthCommand(ManageCommand):
    def _prepare(self, args):
        os.chdir(os.path.abspath(args.path))
        base_dir = os.path.join(self.original_dir, args.path)
        config = json.loads(open(os.path.join(base_dir, './config/repo/web-admin.conf')).read())
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

class CreateUser(_WebAdminAuthCommand):
    """ Creates a new web admin user
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
    class _FakeStdout(object):
        def __init__(self, logger):
            self.logger = logger

        def write(self, msg):
            self.logger.info(msg.strip())

    class _FakeStdin(object):
        def isatty(self):
            return True

    def is_password_required(self):
        return not self.is_interactive

    def before_execute(self, args):
        super(CreateUser, self).before_execute(args)
        self._prepare(args)

        username = getattr(args, 'username', None)
        email = getattr(args, 'email', None)

        if username or email:
            if not(username and email):
                self.logger.error('Both --username and --email are required if either is provided')
                sys.exit(self.SYS_ERROR.INVALID_INPUT)
            else:
                from django.contrib.auth.management.commands.createsuperuser import is_valid_email
                from django.core import exceptions
                self.reset_logger(self.args, True)

                try:
                    is_valid_email(email)
                except exceptions.ValidationError:
                    self.logger.error('Invalid e-mail `%s`', email)
                    sys.exit(self.SYS_ERROR.INVALID_INPUT)
                else:
                    self.is_interactive = False

    def execute(self, args):

        from django.contrib.auth.management.commands.createsuperuser import Command
        self.reset_logger(args, True)

        Command.stdout = CreateUser._FakeStdout(self.logger)
        Command.stdin = CreateUser._FakeStdin()

        options = {'verbosity':0} if self.is_interactive else {
            'username':self.args.username, 'email':self.args.email, 'verbosity':0
        }

        try:
            Command().handle(interactive=self.is_interactive, **options)
        except Exception:
            self.logger.error('Could not create the user, details: `%s`', format_exc())
            sys.exit(self.SYS_ERROR.INVALID_INPUT)
        else:
            self._ok(args)

# ################################################################################################################################

class UpdatePassword(_WebAdminAuthCommand):
    """ Updates a web admin user's password
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
        if getattr(args, 'password'):
            class _Command(Command):
                def _get_pass(self, *ignored_args, **ignored_kwargs):
                    return args.password
        else:
            _Command = Command

        _Command().handle(username=args.username)

        if not called_from_wrapper:
            self._ok(args)

# ################################################################################################################################
