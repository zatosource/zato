# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import json, os

# Zato
from zato.admin.zato_settings import update_globals
from zato.cli import ManageCommand

class _WebAdminAuthCommand(ManageCommand):
    def _prepare(self, args):
        os.chdir(args.path)
        base_dir = os.path.join(self.original_dir, args.path)
        config = json.loads(open(os.path.join(base_dir, './config/repo/web-admin.conf')).read())
        config['config_dir'] = os.path.abspath(args.path)
        update_globals(config, base_dir)
        os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'
        
    def _ok(self, args):
        # Needed because Django took over our logging config
        self.reset_logger(args, True)
        self.logger.info('OK')

class UpdatePassword(_WebAdminAuthCommand):
    """ Updates a web admin user's password
    """
    opts = [
        {'name': 'username', 'help': 'Username to change the password of'},
    ]
    
    def execute(self, args):
        self._prepare(args)
        
        from django.contrib.auth.management.commands.changepassword import Command
        Command().handle(args.username)
        
        self._ok(args)
        
class CreateUser(_WebAdminAuthCommand):
    """ Creates a new web admin user
    """
    class _FakeStdout(object):
        """ django.contrib.auth.management.commands.createsuperuser.Command needs a self.stdout
        so we fake it here
        """
        def __init__(self, logger):
            self.logger = logger
            
        def write(self, msg):
            self.logger.info(msg.strip())
        
    def execute(self, args):
        self._prepare(args)
        
        from django.contrib.auth.management.commands.createsuperuser import Command
        Command.stdout = CreateUser._FakeStdout(self.logger)
        Command().handle(interactive=True)

        self._ok(args)
