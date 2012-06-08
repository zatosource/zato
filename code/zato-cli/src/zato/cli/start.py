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
import json, multiprocessing, os

# ConfigObj
from configobj import ConfigObj

# Zato
from zato.admin.zato_settings import _update_globals
from zato.admin.wsgi_server import main as zato_admin_main
from zato.cli import ManageCommand

zdaemon_conf_name_contents = """<runner>
    program {program}
    socket-name {socket_name}
</runner>
<eventlog>
    <logfile>
        path {logfile_path}
    </logfile>
</eventlog>
"""

class Start(ManageCommand):

    command_name = 'start'
    description = """Starts a Zato component installed in the 'component_dir'. The same command is used for starting servers, load-balancer agents and Zato Admin instances.
component_dir must point to an existing directory into which the given component has been installed.

Examples:
  Assuming a Zato server has been installed in /opt/zato/server1, the command to start the server is 'zato start /opt/zato/server1'.
  If a load-balancer's agent has been installed in /home/zato/lb-agent1, the command to start it is 'zato start /home/zato/lb-agent1'.
"""

    def _on_server(self):

        server_conf = ConfigObj(os.path.join(self.config_dir, 'repo', 'server.conf'))

        parallel_count = int(server_conf['bind']['parallel_count'])
        starting_port = int(server_conf['bind'].get('starting_port'))

        for idx in xrange(parallel_count):

            server_no = '{0}'.format(starting_port+idx).zfill(5)

            socket_name = 'server-{0}.sock'.format(server_no)
            socket_name = os.path.join(self.config_dir, 'zdaemon', socket_name)

            # If we have a socket of that name then we already have a running
            # server, in which case we refrain from starting new processes now.
            if os.path.exists(socket_name):
                msg = 'Server at {0} is already running'.format(self.component_dir)
                print(msg)
                return


        for idx in range(parallel_count):

            server_no = '{0}'.format(starting_port+idx).zfill(5)

            host = 'localhost'
            port = starting_port+idx
            base_dir = self.component_dir
            start_singleton = True if idx == 0 else ''

            zdaemon_conf_name = 'zdaemon-{0}.conf'.format(server_no)
            socket_prefix = 'server-{0}'.format(server_no)
            program = 'python -m zato.server.main {0} {1} {2} {3}'.format(host,
                                            port, base_dir, start_singleton)
            logfile_path_prefix = 'zdaemon-{0}'.format(server_no)

            self._zdaemon_start(zdaemon_conf_name_contents, zdaemon_conf_name, socket_prefix,
                                logfile_path_prefix, program)

        print('Zato server at {0} has been started'.format(self.component_dir))

    def _on_lb(self):

        # Start the agent which will in turn start the load balancer
        config_path = os.path.join(self.config_dir, 'lb-agent.conf')

        zdaemon_conf_name = 'zdaemon-lb.conf'
        socket_prefix = 'lb-agent'
        program = 'python -m zato.agent.load_balancer.main {0}'.format(config_path)
        logfile_path_prefix = 'zdaemon-lb-agent'

        self._zdaemon_start(zdaemon_conf_name_contents, zdaemon_conf_name, socket_prefix,
                            logfile_path_prefix, program)

        # Now start HAProxy.
        config_path = os.path.join(self.config_dir, 'zato.config')

        zdaemon_conf_name = 'zdaemon-haproxy.conf'
        socket_prefix = 'haproxy'
        program = 'haproxy -f {0}'.format(config_path)
        logfile_path_prefix = 'zdaemon-haproxy'

        self._zdaemon_start(zdaemon_conf_name_contents, zdaemon_conf_name, socket_prefix,
                            logfile_path_prefix, program)

        print('Zato load balancer and agent started at {0}'.format(self.component_dir))

    def _on_zato_admin(self):

        # Update Django settings.
        config = json.loads(open('./zato-admin.conf').read())
        config['config_dir'] = os.path.abspath(self.component_dir)
        _update_globals(config)

        # Store the PID so that the server can be later stopped by its PID.
        open('./.zato-admin.pid', 'w').write(str(os.getpid()))

        zato_admin_main(config['host'], config['port'])
        
    def _on_broker(self):
        config_path = os.path.join(self.config_dir, 'repo', 'broker.conf')

        zdaemon_conf_name = 'zdaemon-broker.conf'
        socket_prefix = 'broker'
        program = 'python -m zato.broker.main {0}'.format(config_path)
        logfile_path_prefix = 'zdaemon-broker'
        
        socket_name = 'broker.sock'
        socket_name = os.path.join(self.config_dir, 'zdaemon', socket_name)
        
        if os.path.exists(socket_name):
            msg = 'Broker at {0} is already running'.format(self.component_dir)
            print(msg)
            return

        self._zdaemon_start(zdaemon_conf_name_contents, zdaemon_conf_name, socket_prefix,
                            logfile_path_prefix, program)
        
        print('Broker started at {0}'.format(self.component_dir))
        
def main(target_dir):
    Start(target_dir).run()

if __name__ == '__main__':
    main('.')
