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
import os, signal, sys

# Zato
from zato.cli import ManageCommand

class Stop(ManageCommand):

    command_name = "stop"
    description = "Stops a Zato component"

    def _on_server(self):
        ports_pids = self._zdaemon_command('status')
        if not any(ports_pids.values()):
            print('\nZato server at {0} is not running.\n'.format(self.component_dir))
        else:
            self._zdaemon_command('stop')
            print('\nZato server at {0} has been stopped.\n'.format(self.component_dir))

    def _on_security_server(self):
        ports_pids = self._zdaemon_command('status', ['zdaemon*.conf'])
        if not any(ports_pids.values()):
            print('\nZato security server at {0} is not running.\n'.format(self.component_dir))
        else:
            self._zdaemon_command('stop', ['zdaemon*.conf'])
            print('\nZato security server at {0} has been stopped.\n'.format(self.component_dir))

    def _on_lb(self):
        ports_pids = self._zdaemon_command('status')
        if not any(ports_pids.values()):
            print('\nZato load balancer and agent at {0} are not running.\n'.format(self.component_dir))
        else:
            self._zdaemon_command('stop')
            print('\nZato load balancer and agent at {0} have been stopped.\n'.format(self.component_dir))

    def _on_zato_admin(self):
        pid_file = os.path.join(self.component_dir, ".zato-admin.pid")
        if not os.path.exists(pid_file):
            msg = "\nDid not find the expected file {0}, quitting now.\n".format(pid_file)
            print(msg)
            sys.exit(4) # TODO: Document exit codes

        pid = open(pid_file).read().strip()
        if not pid:
            msg = "\nDid not attempt to stop the ZatoAdmin instance because file {0} is empty.\n".format(pid_file)
            print(msg)
            sys.exit(5) # TODO: Document exit codes

        pid = int(pid)
        msg = "Will now send SIGTERM to pid {0} (as found in the {1} file).".format(pid, pid_file)
        print(msg)

        os.kill(pid, signal.SIGTERM)
        open(pid_file, "w").truncate()

        print("ZatoAdmin stopped OK.")


def main(target_dir):
    Stop(target_dir).run()

if __name__ == "__main__":
    main(".")
