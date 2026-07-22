# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import subprocess
import threading
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# The placeholder in a command that is replaced with the port allocated for the process.
port_placeholder = '{port}'

# How long to wait for a process to exit after terminate before it is killed, in seconds.
stop_timeout = 5

# ################################################################################################################################
# ################################################################################################################################

def allocate_port() -> 'int':
    """ Returns a local TCP port that was free at the time of the call.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        out = sock.getsockname()[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

class Process:
    """ A supervised helper process started with a connector's start_process. The public surface
    is minimal - pid, an allocated local port, is_running and stop. The framework watches the process
    and rebuilds the connection if it dies unexpectedly.
    """

    def __init__(self, command:'strlist', on_died:'callable_') -> 'None':

        # The port allocated for this process - any '{port}' placeholder in the command carries it.
        self.port = allocate_port()

        # What to call when the process dies without stop having been requested.
        self._on_died = on_died

        # Set by stop, which is how the watcher tells an expected exit from a crash.
        self._stop_requested = False

        # Substitute the allocated port into the command and start the process ..
        command = [item.replace(port_placeholder, str(self.port)) for item in command]
        self._popen = subprocess.Popen(command)

        self.pid = self._popen.pid

        # .. and watch it in the background for unexpected exits.
        watcher = threading.Thread(target=self._watch, daemon=True)
        watcher.start()

# ################################################################################################################################

    @property
    def is_running(self) -> 'bool':
        out = self._popen.poll() is None
        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the process - first politely, then by force if it does not exit in time.
        """

        # Let the watcher know this exit is expected.
        self._stop_requested = True

        # There is nothing to do if the process already exited.
        if not self.is_running:
            return

        self._popen.terminate()

        try:
            _ = self._popen.wait(timeout=stop_timeout)
        except subprocess.TimeoutExpired:
            # The process ignored the polite request, so now it is killed outright.
            self._popen.kill()
            _ = self._popen.wait()

# ################################################################################################################################

    def _watch(self) -> 'None':

        # This blocks until the process exits, no matter how.
        _ = self._popen.wait()

        # An exit after stop was requested is expected and needs no reaction.
        if self._stop_requested:
            return

        logger.warning('Helper process pid=%s exited unexpectedly', self.pid)
        self._on_died(self)

# ################################################################################################################################
# ################################################################################################################################
