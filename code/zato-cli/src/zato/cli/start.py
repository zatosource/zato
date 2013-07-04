# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# ConfigObj
from configobj import ConfigObj

# Zato
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
    """ Starts a Zato component installed in the 'path'. The same command is used for starting servers, load-balancer agents and web admin instances.
'path' must point to an existing directory into which the given component has been installed.

Examples:
  - Assuming a Zato server has been installed in /opt/zato/server1, the command to start the server is 'zato start /opt/zato/server1'.
  - If a load-balancer's agent has been installed in /home/zato/lb-agent1, the command to start it is 'zato start /home/zato/lb-agent1'."""
    
    def _on_server(self, show_output=True, *ignored):

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

        if self.show_output:
            if self.verbose:
                self.logger.debug('Zato server at {0} has been started'.format(self.component_dir))
            else:
                self.logger.info('OK')

    def _on_lb(self, *ignored):

        # Start the agent which will in turn start the load balancer
        repo_dir = os.path.join(self.config_dir, 'repo')

        zdaemon_conf_name = 'zdaemon-lb.conf'
        socket_prefix = 'lb-agent'
        program = '{} -m zato.agent.load_balancer.main {}'.format(get_executable(), repo_dir)
        logfile_path_prefix = 'zdaemon-lb-agent'
        
        self._zdaemon_start(zdaemon_conf_name_contents, zdaemon_conf_name, socket_prefix, logfile_path_prefix, program)

        # Now start HAProxy

        if self.show_output:
            if self.verbose:
                self.logger.debug('Zato load balancer and agent started in {0}'.format(self.component_dir))
            else:
                self.logger.info('OK')

    def _on_web_admin(self, *ignored):

        zdaemon_conf_name = 'zdaemon-web-admin.conf'
        socket_prefix = 'web-admin'
        program = '{} -m zato.admin.main'.format(get_executable())
        logfile_path_prefix = 'zdaemon-web-admin'
        
        self._zdaemon_start(zdaemon_conf_name_contents, zdaemon_conf_name, socket_prefix, logfile_path_prefix, program)

        if self.show_output:
            if self.verbose:
                self.logger.debug('Zato web admin started in {0}'.format(self.component_dir))
            else:
                self.logger.info('OK')
