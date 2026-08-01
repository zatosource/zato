# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import subprocess
import threading
import time

# Zato
from _haproxy import Bind_Address, find_free_port, Haproxy_Binary, is_haproxy_available
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from zato.common.typing_ import any_

    any_ = any_
    Popen = Popen

# ################################################################################################################################
# ################################################################################################################################

# The check for HAProxy is the language suite's, re-exported so that a caller of this module has no
# second module to import for it
is_haproxy_available = is_haproxy_available

# What one HAProxy of a test run is configured with. It is written out here rather than taken from
# the file the containers ship with, because that one puts HAProxy in front of a Zato server and
# this puts it in front of a third-party listener, which is the other direction entirely - the
# connection under test is the one leaving Zato, and the proxy is what it goes out through.
_Config_Template = '''\
global
    maxconn 256

defaults
    mode tcp
    timeout connect @connect_timeout@
    timeout client @client_timeout@
    timeout server @server_timeout@

frontend mllp_front
    bind @bind_address@:@front_port@
    default_backend mllp_back

backend mllp_back
    server receiver @bind_address@:@back_port@
'''

# How long HAProxy waits at each stage of a connection. A message the receiving end takes its time
# over must not be cut short by the proxy in the middle, so these are well past anything a test
# holds a connection open for.
_Connect_Timeout = '5s'
_Client_Timeout  = '120s'
_Server_Timeout  = '120s'

# How long HAProxy is given to bind its port before the run is called off
_Startup_Timeout = 20

# How often the port is checked while waiting for it
_Startup_Poll_Interval = 0.2

# How long HAProxy is given to exit once it has been asked to
_Shutdown_Timeout = 5

# How long a check of whether the port is bound waits for the connection
_Port_Check_Timeout = 1.0

# ################################################################################################################################
# ################################################################################################################################

class ProxyHandle:
    """ One HAProxy standing in front of a receiving system, which is how these connections are
    deployed in the field - a sender rarely has the receiver's own address, it has the proxy's.
    """

    def __init__(self, directory:'str', backend_port:'int') -> 'None':

        self.port = find_free_port()
        self.backend_port = backend_port
        self.config_path = os.path.join(directory, f'haproxy-{self.port}.cfg')

        self._process:'subprocess.Popen[bytes] | None' = None

# ################################################################################################################################

    def _write_config(self) -> 'None':
        """ Writes the configuration this instance runs on.
        """
        content = _Config_Template. \
            replace('@bind_address@', Bind_Address). \
            replace('@front_port@', str(self.port)). \
            replace('@back_port@', str(self.backend_port)). \
            replace('@connect_timeout@', _Connect_Timeout). \
            replace('@client_timeout@', _Client_Timeout). \
            replace('@server_timeout@', _Server_Timeout)

        with open(self.config_path, 'w') as config_file:
            _ = config_file.write(content)

# ################################################################################################################################

    def _stream_output(self) -> 'None':
        """ Drains what HAProxy writes so that a full pipe never blocks it, and puts every line in
        this run's own output where a failure can be read back from.
        """
        process = cast_('Popen', self._process)
        output = cast_('any_', process.stdout)

        for line in iter(output.readline, b''):
            text = line.decode('utf8', errors='replace').rstrip()
            print(f'[HAPROXY] {text}')

# ################################################################################################################################

    def _is_port_open(self) -> 'bool':
        """ Returns whether the frontend takes a connection yet.
        """
        probe_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe_socket.settimeout(_Port_Check_Timeout)

        try:
            probe_socket.connect((Bind_Address, self.port))
            out = True
        except OSError:
            out = False
        finally:
            probe_socket.close()

        return out

# ################################################################################################################################

    def start(self) -> 'None':
        """ Runs HAProxy in the foreground and returns once its frontend takes connections.
        """
        self._write_config()

        # The -db flag keeps HAProxy in the foreground, so this handle owns a process it can end
        command = [Haproxy_Binary, '-f', self.config_path, '-db']

        self._process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        output_thread = threading.Thread(target=self._stream_output, daemon=True)
        output_thread.start()

        deadline = time.monotonic() + _Startup_Timeout

        while time.monotonic() < deadline:

            # A configuration HAProxy refuses leaves nothing to wait for, and what it printed on
            # its way out is already in this run's output
            if self._process.poll() is not None:
                raise Exception(f'HAProxy exited with code {self._process.returncode} before it bound its port')

            if self._is_port_open():
                return

            time.sleep(_Startup_Poll_Interval)

        self.stop()
        raise Exception(f'HAProxy did not bind port {self.port} within {_Startup_Timeout}s')

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Ends this instance, killing it outright if it does not go on its own.
        """
        process = self._process

        if process is None:
            return

        if process.poll() is None:

            process.terminate()

            try:
                _ = process.wait(timeout=_Shutdown_Timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                _ = process.wait(timeout=_Shutdown_Timeout)

        self._process = None

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        """ Where an outgoing connection is pointed to reach the listener through this proxy.
        """
        out = f'{Bind_Address}:{self.port}'
        return out

# ################################################################################################################################
# ################################################################################################################################
