# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import os
import sys

# Bunch
from bunch import Bunch

# Zato
from zato.cli import ManageCommand
from zato.cli.check_config import CheckConfig
from zato.cli.stop import Stop
from zato.common import MISC
from zato.common.util import get_haproxy_agent_pidfile
from zato.common.util.proc import start_python_process

# ################################################################################################################################

# During development, it is convenient to configure it here to catch information that should be logged
# even prior to setting up main loggers in each of components.
if 0:
    log_level = logging.INFO
    log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

# ################################################################################################################################

stderr_sleep_fg = 0.9
stderr_sleep_bg = 1.2

# ################################################################################################################################

class Start(ManageCommand):
    """Starts a Zato component installed in the 'path'. The same command is used for starting servers, load-balancer and web admin instances. 'path' must point to a directory into which the given component has been installed. # nopep8

Examples:
  - Assuming a Zato server has been installed in /opt/zato/server1, the command to start the server is 'zato start /opt/zato/server1'.
  - If a load-balancer has been installed in /home/zato/lb1, the command to start it is 'zato start /home/zato/lb1'."""

    opts = [
        {'name':'--fg', 'help':'If given, the component will run in foreground', 'action':'store_true'},
        {'name':'--sync-internal', 'help':"Whether to synchronize component's internal state with ODB", 'action':'store_true'},
        {'name':'--secret-key', 'help':"Component's secret key", 'action':'store'}
    ]

# ################################################################################################################################

    def run_check_config(self):
        cc = CheckConfig(self.args)
        cc.show_output = False
        cc.execute(Bunch({
            'path': '.',
            'ensure_no_pidfile': True,
            'check_server_port_available': True,
            'stdin_data': self.stdin_data,
            'secret_key': self.args.secret_key,
        }))

# ################################################################################################################################

    def delete_pidfile(self):
        try:
            path = os.path.join(self.component_dir, MISC.PIDFILE)
            os.remove(path)
        except Exception as e:
            self.logger.info('Pidfile `%s` could not be deleted `%s`', path, e)

# ################################################################################################################################

    def check_pidfile(self, pidfile=None):
        pidfile = pidfile or os.path.join(self.config_dir, MISC.PIDFILE)

        # If we have a pidfile of that name then we already have a running
        # server, in which case we refrain from starting new processes now.
        if os.path.exists(pidfile):
            msg = 'Error - found pidfile `{}`'.format(pidfile)
            self.logger.info(msg)
            return self.SYS_ERROR.COMPONENT_ALREADY_RUNNING

        # Returning None would have sufficed but let's be explicit.
        return 0

# ################################################################################################################################

    def start_component(self, py_path, name, program_dir, on_keyboard_interrupt=None):
        """ Starts a component in background or foreground, depending on the 'fg' flag.
        """
        start_python_process(
            name, self.args.fg, py_path, program_dir, on_keyboard_interrupt, self.SYS_ERROR.FAILED_TO_START, {
                'sync_internal': self.args.sync_internal,
                'secret_key': self.args.secret_key or ''
            }, stdin_data=self.stdin_data)

        if self.show_output:
            if not self.args.fg and self.verbose:
                self.logger.debug('Zato {} `{}` starting in background'.format(name, self.component_dir))
            else:
                self.logger.info('OK')

# ################################################################################################################################

    def _on_server(self, show_output=True, *ignored):
        self.run_check_config()
        self.start_component('zato.server.main', 'server', self.component_dir, self.delete_pidfile)

# ################################################################################################################################

    def _on_lb(self, *ignored):
        self.run_check_config()

        def stop_haproxy():
            Stop(self.args).stop_haproxy(self.component_dir)

        found_pidfile = self.check_pidfile()
        if not found_pidfile:
            found_agent_pidfile = self.check_pidfile(get_haproxy_agent_pidfile(self.component_dir))
            if not found_agent_pidfile:
                self.start_component(
                    'zato.agent.load_balancer.main', 'load-balancer', os.path.join(self.config_dir, 'repo'), stop_haproxy)
                return

        # Will be returned if either of pidfiles was found
        sys.exit(self.SYS_ERROR.FOUND_PIDFILE)

# ################################################################################################################################

    def _on_web_admin(self, *ignored):
        self.run_check_config()
        self.start_component('zato.admin.main', 'web-admin', '', self.delete_pidfile)

# ################################################################################################################################

    def _on_scheduler(self, *ignored):
        self.run_check_config()
        self.check_pidfile()
        self.start_component('zato.scheduler.main', 'scheduler', '', self.delete_pidfile)

# ################################################################################################################################
