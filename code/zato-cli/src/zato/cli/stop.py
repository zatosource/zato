# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.cli import ManageCommand
from zato.common.util.open_ import open_r

# ################################################################################################################################
# ################################################################################################################################

class Stop(ManageCommand):
    """ Stops a Zato component
    """
    def signal(self, component_name, signal_name, signal_code, pidfile=None, component_dir=None, ignore_missing=False,
        needs_logging=True):
        """ Sends a signal to a process known by its pidfile.
        """

        # stdlib
        import os
        import sys

        component_dir = component_dir or self.component_dir
        pidfile = pidfile or os.path.join(component_dir, 'pidfile')

        if not os.path.exists(pidfile):
            if ignore_missing:
                # No such pidfile - it may be a connector process and these are optional,
                # in this case, we just simply return because there is not anything else for us to do.
                return

            self.logger.error('No pidfile found in `%s`', pidfile)
            sys.exit(self.SYS_ERROR.FILE_MISSING)

        pid = open_r(pidfile).read().strip()
        if not pid:
            self.logger.error('Empty pidfile `%s`, did not attempt to stop `%s`', pidfile, component_dir)
            sys.exit(self.SYS_ERROR.NO_PID_FOUND)

        pid = int(pid)
        if needs_logging:
            self.logger.debug('Sending `%s` to pid `%s` (found in `%s`)', signal_name, pid, pidfile)

        os.kill(pid, signal_code)
        os.remove(pidfile)

        if needs_logging:
            self.logger.info('%s `%s` shutting down', component_name, component_dir)

# ################################################################################################################################

    def _on_server(self, *ignored):

        # stdlib
        import signal

        self.signal('Server', 'SIGTERM', signal.SIGTERM)

# ################################################################################################################################

    def _on_web_admin(self, *ignored):

        # stdlib
        import signal

        self.signal('Web admin', 'SIGTERM', signal.SIGTERM)

# ################################################################################################################################

    def _on_scheduler(self, *ignored):

        # stdlib
        import signal

        self.signal('Scheduler', 'SIGTERM', signal.SIGTERM)

# ################################################################################################################################
# ################################################################################################################################
