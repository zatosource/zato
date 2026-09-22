# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import socket
import subprocess
import threading
import time
from typing import NamedTuple

# Zato
from zato.common.hl7.mllp.haproxy import Env_Port_Name

# Live environment
from live_environment.quickstart import find_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The configuration the containers ship with, which is what a suite runs so that its tests exercise the
# same frontend, the same backend and the same PROXY protocol options as production.
_Template_Path = os.path.join(
    os.environ['ZATO_TEST_BASE_DIR'], 'code', 'zato-common', 'src', 'zato', 'common', 'pubsub', 'server', 'haproxy.cfg')

# The binary a suite runs - absent from a machine that never installed it, which is what a suite checks
# for before it decides whether to skip.
Haproxy_Binary = 'haproxy'

# What a suite whose senders are all on this machine binds to
Loopback_Address = '127.0.0.1'

# What a suite whose senders are containers binds to - the containers reach the host through its
# bridge address, which a loopback bind never answers on
Every_Interface = '0.0.0.0'

# What the shipped configuration binds on every interface, and so what has to be moved out of the way
# before a suite can bind it without colliding with whatever else is on this machine.
_Fixed_Internal_Port = '11225'

# The path the shipped configuration reads its blocked paths from, which exists in a container only
_Blocked_Paths_Path = '/opt/zato/env/qs-1/blocked-paths.txt'

# How long HAProxy is given to bind its ports before the run is called off
_Startup_Timeout = 20

# How often the ports are checked while waiting for them
_Startup_Poll_Interval = 0.2

# How long HAProxy is given to exit once it has been asked to
_Shutdown_Timeout = 5

# How long a check of whether a port is open waits for the connection
_Port_Check_Timeout = 1.0

# ################################################################################################################################
# ################################################################################################################################

class TLSBind(NamedTuple):
    """ What the TLS bind presents and verifies senders against.
    """

    # The server certificate and its key in one file, as HAProxy reads them
    pem_path: 'str'

    # The authority a sender's certificate has to have been issued by
    ca_cert_path: 'str'

# ################################################################################################################################

class HAProxyPorts(NamedTuple):
    """ The ports one HAProxy instance listens on.
    """

    # Where a sender connects over a plain connection
    mllp_plain: 'int'

    # Where a sender connects over TLS, presenting a certificate that is verified here - zero when
    # the instance has no TLS bind
    mllp_tls: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _is_port_open(port:'int') -> 'bool':
    """ Returns whether something accepts a connection on the port.
    """
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(_Port_Check_Timeout)

    try:
        test_socket.connect((Loopback_Address, port))
        test_socket.close()
        out = True
    except OSError:
        out = False

    return out

# ################################################################################################################################

def is_haproxy_available() -> 'bool':
    """ Returns whether the HAProxy binary is on this machine at all.
    """
    out = bool(shutil.which(Haproxy_Binary))
    return out

# ################################################################################################################################

def _build_tls_bind_line(bind_address:'str', port:'int', tls_bind:'TLSBind') -> 'str':
    """ The MLLP TLS bind as the container's own SSL configuration builds it - the server certificate, the
    authority to verify a sender against, and verification required.
    """
    out = f'    bind {bind_address}:{port} ssl crt {tls_bind.pem_path}' + \
        f' ca-file {tls_bind.ca_cert_path} verify required'

    return out

# ################################################################################################################################

def _render_config(
    config_path:'str',
    blocked_paths_path:'str',
    bind_address:'str',
    ports:'HAProxyPorts',
    tls_bind:'TLSBind | None',
) -> 'None':
    """ Writes one instance's configuration file out of the one the containers ship with, changed only
    where a test run cannot use what a container uses.
    """
    with open(_Template_Path, 'r') as template_file:
        content = template_file.read()

    # A container owns every interface it has, whereas this runs on a machine that is somebody's own
    content = content.replace(f'{Every_Interface}:', f'{Loopback_Address}:')

    # The loopback hop between the two HTTP frontends has a port hard-coded in the shipped file,
    # and that port may well belong to something already running here
    content = content.replace(_Fixed_Internal_Port, str(find_free_port()))

    # The list of paths to turn away lives at a container path, so the run points at its own copy
    content = content.replace(_Blocked_Paths_Path, blocked_paths_path)

    # The MLLP bind alone goes where the suite's senders can reach it - the HTTP frontends stay on loopback
    loopback_bind_line = f'    bind {Loopback_Address}:${{Zato_Port_MLLP}}'
    plain_bind_line = f'    bind {bind_address}:${{Zato_Port_MLLP}}'

    if loopback_bind_line not in content:
        raise Exception(f'No MLLP bind line in {_Template_Path}')

    bind_lines = plain_bind_line

    # The TLS bind is not in the shipped file - a container's SSL configuration adds it once
    # certificates are mounted, and this is the same bind that step builds
    if tls_bind:
        tls_bind_line = _build_tls_bind_line(bind_address, ports.mllp_tls, tls_bind)
        bind_lines = plain_bind_line + '\n' + tls_bind_line

    content = content.replace(loopback_bind_line, bind_lines)

    with open(config_path, 'w') as config_file:
        _ = config_file.write(content)

# ################################################################################################################################
# ################################################################################################################################

class HAProxyHandle:
    """ One HAProxy instance running for the duration of a suite.
    """

    def __init__(self, ports:'HAProxyPorts', config_path:'str', mllp_internal_port:'int') -> 'None':
        self.ports = ports
        self.config_path = config_path
        self.mllp_internal_port = mllp_internal_port
        self.process:'subprocess.Popen[bytes] | None' = None

# ################################################################################################################################

    def _stream_output(self) -> 'None':
        """ Drains what HAProxy writes so that a full pipe buffer never blocks it, and puts every line
        in the suite's own output where a failing run can be read back from.
        """
        process:'any_' = self.process

        for line in iter(process.stdout.readline, b''):
            text = line.decode('utf8', errors='replace').rstrip()
            print(f'[HAPROXY] {text}')

# ################################################################################################################################

    def _build_environment(self) -> 'dict':
        """ The configuration reads every port and password from the environment, as the container's entry point
        supplies them - only the MLLP port matters here, the rest are there for the file to parse.
        """
        out = os.environ.copy()

        out['Zato_Port_MLLP'] = str(self.ports.mllp_plain)
        out[Env_Port_Name] = str(self.mllp_internal_port)
        out['Zato_Port_Server'] = str(find_free_port())
        out['Zato_Port_Dashboard'] = str(find_free_port())
        out['Zato_Port_OpenAPI_Console'] = str(find_free_port())
        out['Zato_Port_Load_Balancer'] = str(find_free_port())

        return out

# ################################################################################################################################

    def _are_ports_open(self) -> 'bool':
        """ True once every bind this instance has accepts a connection.
        """
        if not _is_port_open(self.ports.mllp_plain):
            return False

        if self.ports.mllp_tls:
            out = _is_port_open(self.ports.mllp_tls)
        else:
            out = True

        return out

# ################################################################################################################################

    def start(self) -> 'None':
        """ Runs HAProxy in the foreground and waits for its MLLP ports to accept a connection.
        """

        # The -db flag keeps HAProxy in the foreground, so the handle owns a process it can end
        command = [Haproxy_Binary, '-f', self.config_path, '-db']

        self.process = subprocess.Popen(
            command,
            env=self._build_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        output_thread = threading.Thread(target=self._stream_output, daemon=True)
        output_thread.start()

        deadline = time.monotonic() + _Startup_Timeout

        while time.monotonic() < deadline:

            # A configuration HAProxy refuses leaves nothing to wait for, so the run is called off
            # with whatever it printed already in the suite's output
            if self.process.poll() is not None:
                raise Exception(f'HAProxy exited with code {self.process.returncode} before it bound its ports')

            if self._are_ports_open():
                return

            time.sleep(_Startup_Poll_Interval)

        self.stop()
        raise Exception(f'HAProxy did not bind its MLLP ports within {_Startup_Timeout}s')

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Ends the HAProxy instance, killing it outright if it does not go on its own.
        """
        process = self.process

        if not process:
            return

        if process.poll() is None:

            process.terminate()

            try:
                _ = process.wait(timeout=_Shutdown_Timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                _ = process.wait(timeout=_Shutdown_Timeout)

        self.process = None

# ################################################################################################################################
# ################################################################################################################################

def start_haproxy(
    directory:'str',
    mllp_internal_port:'int',
    *,
    bind_address:'str',
    tls_bind:'TLSBind | None'=None,
) -> 'HAProxyHandle':
    """ Renders the configuration and starts HAProxy on it - the internal port is the server's own MLLP listener
    the backend forwards to, the bind address is where senders connect.
    """
    config_path = os.path.join(directory, 'haproxy.cfg')
    blocked_paths_path = os.path.join(directory, 'blocked-paths.txt')

    # The configuration turns away requests whose path is in this file, and HAProxy refuses to
    # start when a file an ACL names is missing, so an empty one stands in for the container's
    with open(blocked_paths_path, 'w') as blocked_paths_file:
        _ = blocked_paths_file.write('')

    if tls_bind:
        mllp_tls = find_free_port()
    else:
        mllp_tls = 0

    ports = HAProxyPorts(
        mllp_plain=find_free_port(),
        mllp_tls=mllp_tls,
    )

    _render_config(config_path, blocked_paths_path, bind_address, ports, tls_bind)

    out = HAProxyHandle(ports, config_path, mllp_internal_port)
    out.start()

    return out

# ################################################################################################################################
# ################################################################################################################################
