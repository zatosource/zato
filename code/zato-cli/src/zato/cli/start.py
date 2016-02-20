# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, sys
from tempfile import mkstemp
from time import time, sleep

# Bunch
from bunch import Bunch

# Sarge
from sarge import run

# Zato
from zato.cli import ManageCommand
from zato.cli.check_config import CheckConfig
from zato.cli.stop import Stop
from zato.common import MISC
from zato.common.util import get_executable, get_haproxy_pidfile

stderr_sleep_fg = 0.9
stderr_sleep_bg = 1.2

class _StdErr(object):
    def __init__(self, path, timeout):
        self.path = path
        self.timeout = timeout

    def wait_for_error(self):
        now = time()

        while time() - now < self.timeout:
            sleep(0.02)
            _stderr = open(self.path)
            _err = _stderr.read()
            if _err:
                return _err
            else:
                _stderr.close()

class Start(ManageCommand):
    """Starts a Zato component installed in the 'path'. The same command is used for starting servers, load-balancer and web admin instances. 'path' must point to a directory into which the given component has been installed. # nopep8

Examples:
  - Assuming a Zato server has been installed in /opt/zato/server1, the command to start the server is 'zato start /opt/zato/server1'.
  - If a load-balancer has been installed in /home/zato/lb1, the command to start it is 'zato start /home/zato/lb1'."""

    opts = [
        {'name':'--fg', 'help':'If given, the component will run in foreground', 'action':'store_true'}
    ]

    def run_check_config(self):
        cc = CheckConfig(self.args)
        cc.show_output = False
        cc.execute(Bunch(path='.', ensure_no_pidfile=True, check_server_port_available=True))

    def delete_pidfile(self):
        os.remove(os.path.join(self.component_dir, MISC.PIDFILE))

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

    def start_component(self, py_path, name, program_dir, on_keyboard_interrupt=None):
        """ Starts a component in background or foreground, depending on the 'fg' flag.
        """
        tmp_path = mkstemp('-zato-start-{}.txt'.format(name.replace(' ','')))[1]
        stdout_redirect = '' if self.args.fg else '1> /dev/null'
        stderr_redirect = '2> {}'.format(tmp_path)
        program = '{} -m {} {} {} {}'.format(get_executable(), py_path, program_dir, stdout_redirect, stderr_redirect)
        try:
            _stderr = _StdErr(
                tmp_path, stderr_sleep_fg if self.args.fg else stderr_sleep_bg)

            run(program, async=False if self.args.fg else True)

            # Wait a moment for any potential errors
            _err = _stderr.wait_for_error()
            if _err:
                self.logger.warn(_err)
                sys.exit(self.SYS_ERROR.FAILED_TO_START)

        except KeyboardInterrupt:
            if on_keyboard_interrupt:
                on_keyboard_interrupt()
            sys.exit(0)

        if self.show_output:
            if not self.args.fg and self.verbose:
                self.logger.debug('Zato {} `{}` starting in background'.format(name, self.component_dir))
            else:
                self.logger.info('OK')

    def _on_server(self, show_output=True, *ignored):
        self.run_check_config()
        self.start_component('zato.server.main', 'server', self.component_dir, self.delete_pidfile)

    def _on_lb(self, *ignored):
        self.run_check_config()

        def stop_haproxy():
            Stop(self.args).stop_haproxy(self.component_dir)

        found_pidfile = self.check_pidfile()
        if not found_pidfile:
            found_pidfile = self.check_pidfile(get_haproxy_pidfile(self.component_dir))
            if not found_pidfile:
                self.start_component(
                    'zato.agent.load_balancer.main', 'load-balancer', os.path.join(self.config_dir, 'repo'), stop_haproxy)

        sys.exit(found_pidfile)

    def _on_web_admin(self, *ignored):
        self.run_check_config()
        self.start_component('zato.admin.main', 'web admin', '', self.delete_pidfile)
