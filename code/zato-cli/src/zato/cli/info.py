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

# Zato
from zato.cli import ManageCommand

class Info(ManageCommand):
    """ Shows detailed information regarding a chosen Zato component
    """
    def _on_server(self):

        ports_pids = self._zdaemon_command('status')
        pids = ports_pids.values()

        if all(pids):
            parallel_status = 'is running'
        elif any(pids):
            parallel_status = 'is running but some processes are missing'
        else:
            parallel_status = 'is not running'

        msg = '\nZato server at {0} {1}.\n'.format(self.component_dir, parallel_status)
        msg += '\nParallel servers:'
        for idx, (port, pid) in enumerate(sorted(ports_pids.items())):
            pid_info = 'PID ' + pid if pid else '(process not running)'
            msg += '\n {0}) port {1}, {2}'.format(idx+1, port, pid_info)

        msg += '\n'

        print(msg)


    def _on_lb_agent(self):
        pass

    def _on_zato_admin(self):
        pass

def main(target_dir):
    Info(target_dir).run()

if __name__ == '__main__':
    main('.')
