# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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
import json, os, signal, sys

# Zato
from zato.cli import ManageCommand

class Stop(ManageCommand):

    def _signal(self, pid_file, component_name, signal_name, signal_code):
        """ Sends a signal to a process known by its ID.
        """
        if not os.path.exists(pid_file):
            self.logger.error('Did not find the expected file {}, quitting now'.format(pid_file))
            sys.exit(self.SYS_ERROR.FILE_MISSING)

        pid = open(pid_file).read().strip()
        if not pid:
            self.logger.error('Did not attempt to stop the {} because the file {} is empty'.format(component_name, pid_file))
            sys.exit(self.SYS_ERROR.NO_PID_FOUND)

        pid = int(pid)
        self.logger.debug('Will now send {} to pid {} (as found in the {} file)'.format(signal_name, pid, pid_file))

        os.kill(pid, signal_code)
        open(pid_file, 'w').truncate()

    def _on_server(self):
        ports_pids = self._zdaemon_command('status')
        if not any(ports_pids.values()):
            self.logger.warn('No Zato server running in {}'.format(self.component_dir))
        else:
            self._zdaemon_command('stop')
            self.logger.info('Stopped Zato server in {}'.format(self.component_dir))

    def _on_lb(self):
        ports_pids = self._zdaemon_command('status')
        if not any(ports_pids.values()):
            self.logger.warn('Zato load-balancer and agent at {} are not running'.format(self.component_dir))
        else:
            # Stops the load balancer
            json_config = json.loads(open(os.path.join(self.component_dir, 'config', 'lb-agent.conf')).read())
            pid_file = os.path.abspath(os.path.join(self.component_dir, json_config['pid_file']))
            self._signal(pid_file, 'load-balancer', 'SIGUSR1', signal.SIGUSR1)
            
            # Stops the agent
            self._zdaemon_command('stop')
            self.logger.info('Stopped load-balancer and agent in {}'.format(self.component_dir))

    def _on_zato_admin(self):
        ports_pids = self._zdaemon_command('status')
        if not any(ports_pids.values()):
            self.logger.warn('No ZatoAdmin running in {}'.format(self.component_dir))
        else:
            self._zdaemon_command('stop')
            self.logger.info('Stopped ZatoAdmin in {}'.format(self.component_dir))
