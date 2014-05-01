# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, sys

# Bunch
from bunch import Bunch

# ConfigObj
from configobj import ConfigObj

# Sarge
from sarge import capture_both, run

# Zato
from zato.cli import ManageCommand
from zato.cli.check_config import CheckConfig
from zato.common.util import get_executable

class Start(ManageCommand):
    """Starts a Zato component installed in the 'path'. The same command is used for starting servers, load-balancer and web admin instances. 'path' must point to a directory into which the given component has been installed.

Examples:
  - Assuming a Zato server has been installed in /opt/zato/server1, the command to start the server is 'zato start /opt/zato/server1'.
  - If a load-balancer has been installed in /home/zato/lb1, the command to start it is 'zato start /home/zato/lb1'."""

    opts = [
        {'name':'--fg', 'help':'If given, the component will run in foreground', 'action':'store_true'}
    ]

    def check_pidfile(self):

        pidfile = os.path.join(self.config_dir, 'pidfile')

        # If we have a pidfile of that name then we already have a running
        # server, in which case we refrain from starting new processes now.
        if os.path.exists(pidfile):
            msg = 'Error - found pidfile `{}`'.format(self.pidfile)
            self.logger.info(msg)
            return self.SYS_ERROR.COMPONENT_ALREADY_RUNNING

    def start_component(self, py_path, name, program_dir):
        """ Starts a component in background or foreground, depending on the 'fg' flag.
        """
        program = '{} -m {} {}'.format(get_executable(), py_path, program_dir)
        func, async = (run, False) if self.args.fg else (capture_both, True)
        
        try:
            func(program, async=async)
        except KeyboardInterrupt:
            sys.exit(0)

        if self.show_output:
            if not self.args.fg and self.verbose:
                self.logger.debug('Zato {} `{}` starting in background'.format(name, self.component_dir))
            else:
                self.logger.info('OK')

    def _on_server(self, show_output=True, *ignored):

        # Perhaps it's already running
        #self.check_pidfile()

        # Check config before starting anything
        cc = CheckConfig(self.args)
        cc.show_output = False
        cc.execute(Bunch(path='.'))

        # Good to go now
        self.start_component('zato.server.main', 'server', self.component_dir)

    def _on_lb(self, *ignored):

        # TODO: Starting it in foreground means we need to remember about haproxy still being started in background
        self.start_component('zato.agent.load_balancer.main', 'load-balancer', os.path.join(self.config_dir, 'repo'))

    def _on_web_admin(self, *ignored):
        self.start_component('zato.admin.main', 'load-balancer', '')
