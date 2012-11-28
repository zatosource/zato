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
import json, os, sys

# ConfigObj
from configobj import ConfigObj

# Zato
from zato.admin.zato_settings import _update_globals
from zato.admin.wsgi_server import main as zato_admin_main
from zato.cli import ManageCommand
from zato.common.util import get_executable

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

    def _on_server(self, show_output=True):

        server_conf = ConfigObj(os.path.join(self.config_dir, 'repo', 'server.conf'))
        port = server_conf['main']['gunicorn_bind'].split(':')[1]
        server_prefix = '{0}'.format(port).zfill(5)

        socket_name = 'server-{0}.sock'.format(server_prefix)
        socket_name = os.path.join(self.config_dir, 'zdaemon', socket_name)

        # If we have a socket of that name then we already have a running
        # server, in which case we refrain from starting new processes now.
        if os.path.exists(socket_name):
            msg = 'Server at {0} is already running'.format(self.component_dir)
            self.logger.debug(msg)
            return self.SYS_ERROR.COMPONENT_ALREADY_RUNNING

        zdaemon_conf_name = 'zdaemon-{0}.conf'.format(port)
        socket_prefix = 'server-{0}'.format(port)
        program = '{} -m zato.server.main {}'.format(get_executable(), self.component_dir)
        logfile_path_prefix = 'zdaemon-{}'.format(port)

        self._zdaemon_start(zdaemon_conf_name_contents, zdaemon_conf_name, socket_prefix,
                            logfile_path_prefix, program)

        if self.verbose:
            self.logger.debug('Zato server at {0} has been started'.format(self.component_dir))
        else:
            self.logger.info('OK')

    def _on_lb(self):

        # Start the agent which will in turn start the load balancer
        config_path = os.path.join(self.config_dir, 'lb-agent.conf')

        zdaemon_conf_name = 'zdaemon-lb.conf'
        socket_prefix = 'lb-agent'
        program = '{} -m zato.agent.load_balancer.main {}'.format(get_executable(), config_path)
        logfile_path_prefix = 'zdaemon-lb-agent'
        
        self._zdaemon_start(zdaemon_conf_name_contents, zdaemon_conf_name, socket_prefix, logfile_path_prefix, program)

        # Now start HAProxy

        if self.verbose:
            self.logger.debug('Zato load balancer and agent started in {0}'.format(self.component_dir))
        else:
            self.logger.info('OK')

    def _on_zato_admin(self):

        # Update Django settings.
        config = json.loads(open('./config/repo/zato-admin.conf').read())
        config['config_dir'] = os.path.abspath(self.component_dir)
        _update_globals(config)

        # Store the PID so that the server can be later stopped by its PID.
        open('./.zato-admin.pid', 'w').write(str(os.getpid()))

        zato_admin_main(config['host'], config['port'], self.component_dir)
