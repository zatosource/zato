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

    command_name = 'stop'
    description = 'Stops a Zato component'
    
    def _signal(self, pid_file, component_name, signal_name, signal_code):
        """ Sends a signal to a process known by its ID.
        """
        if not os.path.exists(pid_file):
            msg = 'Did not find the expected file {0}, quitting now'.format(pid_file)
            print(msg)
            sys.exit(4) # TODO: Document exit codes

        pid = open(pid_file).read().strip()
        if not pid:
            msg = 'Did not attempt to stop the {} because the file {} is empty'.format(component_name, pid_file)
            print(msg)
            sys.exit(5) # TODO: Document exit codes

        pid = int(pid)
        msg = 'Will now send {} to pid {} (as found in the {} file)'.format(signal_name, pid, pid_file)
        print(msg)

        os.kill(pid, signal_code)
        open(pid_file, 'w').truncate()

    def _on_server(self):
        ports_pids = self._zdaemon_command('status')
        if not any(ports_pids.values()):
            print('Zato server at {0} is not running'.format(self.component_dir))
        else:
            self._zdaemon_command('stop')
            print('Zato server at {0} has been stopped'.format(self.component_dir))

    def _on_lb(self):
        ports_pids = self._zdaemon_command('status')
        if not any(ports_pids.values()):
            print('Zato load balancer and agent at {0} are not running'.format(self.component_dir))
        else:
            # Stops the load balancer
            json_config = json.loads(open(os.path.join(self.component_dir, 'config', 'lb-agent.conf')).read())
            pid_file = os.path.abspath(os.path.join(self.component_dir, json_config['pid_file']))
            self._signal(pid_file, 'load balancer', 'SIGUSR1', signal.SIGUSR1)
            
            # Stops the agent
            self._zdaemon_command('stop')
            print('Zato load balancer and agent at {0} have been stopped'.format(self.component_dir))

    def _on_zato_admin(self):
        self._signal(os.path.join(self.component_dir, '.zato-admin.pid'), 'ZatoAdmin instance', 'SIGTERM', signal.SIGTERM)
        print('ZatoAdmin stopped OK.')
        
    def _on_broker(self):
        ports_pids = self._zdaemon_command('status')
        if not any(ports_pids.values()):
            print('Broker at {0} is not running'.format(self.component_dir))
        else:
            self._zdaemon_command('stop')
            print('Broker at {0} has been stopped'.format(self.component_dir))


def main(target_dir):
    Stop(target_dir).run()

if __name__ == '__main__':
    main('.')
