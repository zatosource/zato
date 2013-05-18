# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import json, os, signal, sys

# Zato
from zato.cli import ManageCommand

class Stop(ManageCommand):
    """ Stops a Zato component
    """
    def _try_stop(self, no_pid_template, stop_template, pre_stop_func=None):
        ports_pids = self._zdaemon_command('status')
        if not any(ports_pids.values()):
            if self.show_output:
                self.logger.warn(no_pid_template.format(self.component_dir))
        else:
            if pre_stop_func:
                pre_stop_func()
                
            self._zdaemon_command('stop')
            if self.show_output:
                self.logger.info(stop_template.format(self.component_dir))
    
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

    def _on_server(self, *ignored):
        self._try_stop('No Zato server running in {}', 'Stopped Zato server in {}')

    def _on_lb(self, *ignored):
        def stop_haproxy():
            json_config = json.loads(open(os.path.join(self.component_dir, 'config', 'repo', 'lb-agent.conf')).read())
            pid_file = os.path.abspath(os.path.join(self.component_dir, json_config['pid_file']))
            self._signal(pid_file, 'load-balancer', 'SIGUSR1', signal.SIGUSR1)
            
        self._try_stop('Zato load-balancer and agent in {} are not running', 'Stopped load-balancer and agent in {}', stop_haproxy)

    def _on_web_admin(self, *ignored):
        self._try_stop('No web admin running in {}', 'Stopped web admin in {}')
