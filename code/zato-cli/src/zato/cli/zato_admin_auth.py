# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import json, os

# Zato
from zato.admin.zato_settings import update_globals
from zato.cli import ManageCommand

class _ZatoAdminAuthCommand(ManageCommand):
    def _prepare(self, args):
        os.chdir(args.path)
        base_dir = os.path.join(self.original_dir, args.path)
        config = json.loads(open(os.path.join(base_dir, './config/repo/zato-admin.conf')).read())
        config['config_dir'] = os.path.abspath(args.path)
        update_globals(config, base_dir)
        os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'

class UpdatePassword(_ZatoAdminAuthCommand):
    """ Updates a Zato admin user's password
    """
    opts = [
        {'name': 'username', 'help': 'Username to change the password of'},
    ]
    def execute(self, args):
        self._prepare(args)
        
        from django.contrib.auth.management.commands.changepassword import Command
        Command().handle(args.username)

class CreateUser(_ZatoAdminAuthCommand):
    """ Creates a new Zato admin user
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
