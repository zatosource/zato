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
from zato.common.crypto.api import CryptoManager
from zato.common.hl7.mllp.haproxy import Env_Port_Name
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _certs import TestCertificates
    from zato.common.typing_ import any_

    any_ = any_
    TestCertificates = TestCertificates

# ################################################################################################################################
# ################################################################################################################################

# The configuration the containers ship with, which is what this suite runs so that the tests
# exercise the same frontend, the same backend and the same PROXY protocol options as production.
_Template_Path = os.path.join(
    os.environ['ZATO_TEST_BASE_DIR'], 'code', 'zato-common', 'src', 'zato', 'common', 'pubsub', 'server', 'haproxy.cfg')

# The binary the tests run - absent from a machine that never installed it, which is what the
# suite checks for before it decides whether to skip.
Haproxy_Binary = 'haproxy'

# The loopback address everything here binds to. The shipped configuration binds every interface,
# which is right for a container and wrong for a test run on somebody's own machine.
Bind_Address = '127.0.0.1'

# What the shipped configuration binds on every interface, and so what has to be moved out of
# the way before a test run can bind it without colliding with whatever else is on this machine.
_Fixed_Internal_Port = '11225'
_Fixed_Stats_Bind    = 'bind *:${Zato_Port_Load_Balancer_Stats}'

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

# How many bits the passwords the statistics listener asks for are made of. Nothing in a test run
# ever reads that listener, so these exist only because the configuration will not parse without them.
_Password_Bits = 256

# ################################################################################################################################
# ################################################################################################################################

class HAProxyPorts(NamedTuple):
    """ The ports one HAProxy instance of a test run listens on.
    """

    # Where a client sends HL7 over a plain connection
    mllp_plain: 'int'

    # Where a client sends HL7 over TLS, presenting a certificate that is verified here
    mllp_tls: 'int'

# ################################################################################################################################
# ################################################################################################################################

def find_free_port() -> 'int':
    """ Asks the operating system for a port nothing is listening on.
    """
    temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temporary_socket.bind((Bind_Address, 0))

    _, port = temporary_socket.getsockname()
    temporary_socket.close()

    out = port
    return out

# ################################################################################################################################

def _is_port_open(port:'int') -> 'bool':
    """ Returns whether something accepts a connection on the port.
    """
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(_Port_Check_Timeout)

    try:
        test_socket.connect((Bind_Address, port))
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

def _build_tls_bind_line(port:'int', certificates:'TestCertificates') -> 'str':
    """ Builds the MLLP TLS bind exactly as the container's own SSL configuration builds it - the
    server certificate on the bind, the authority to verify a sender against, and verification
    required, which is what makes the common name reach the listener on the PROXY header.
    """
    out = f'    bind {Bind_Address}:{port} ssl crt {certificates.haproxy_pem_path}' + \
        f' ca-file {certificates.ca_cert_path} verify required'

    return out

# ################################################################################################################################

def _render_config(
    config_path:'str',
    blocked_paths_path:'str',
    ports:'HAProxyPorts',
    certificates:'TestCertificates',
) -> 'None':
    """ Writes the test run's configuration file out of the one the containers ship with, changed
    only where a test run cannot use what a container uses.
    """
    with open(_Template_Path, 'r') as template_file:
        content = template_file.read()

    # A container owns every interface it has, whereas this runs on a machine that is somebody's own
    content = content.replace('0.0.0.0:', f'{Bind_Address}:')

    # The loopback hop between the two HTTP frontends has a port hard-coded in the shipped file,
    # and that port may well belong to something already running here
    content = content.replace(_Fixed_Internal_Port, str(find_free_port()))

    # The statistics listener binds every interface, so a test run gives it the loopback and its own port
    content = content.replace(_Fixed_Stats_Bind, f'bind {Bind_Address}:{find_free_port()}')

    # The list of paths to turn away lives at a container path, so the run points at its own copy
    content = content.replace(_Blocked_Paths_Path, blocked_paths_path)

    # The TLS bind is not in the shipped file - a container's SSL configuration adds it once
    # certificates are mounted, and this is the same bind that step builds
    plain_bind_line = f'    bind {Bind_Address}:${{Zato_Port_MLLP}}'

    if plain_bind_line not in content:
        raise Exception(f'No MLLP bind line to add the TLS bind after in {_Template_Path}')

    tls_bind_line = _build_tls_bind_line(ports.mllp_tls, certificates)
    content = content.replace(plain_bind_line, plain_bind_line + '\n' + tls_bind_line)

    with open(config_path, 'w') as config_file:
        _ = config_file.write(content)

# ################################################################################################################################
# ################################################################################################################################

class HAProxyHandle:
    """ One HAProxy instance running for the duration of a test run.
    """

    def __init__(self, ports:'HAProxyPorts', config_path:'str', mllp_internal_port:'int') -> 'None':
        self.ports = ports
        self.config_path = config_path
        self.mllp_internal_port = mllp_internal_port
        self.process:'subprocess.Popen[bytes] | None' = None

# ################################################################################################################################

    def _stream_output(self) -> 'None':
        """ Drains what HAProxy writes so that a full pipe buffer never blocks it, and puts every
        line in the test's own output where a failing run can be read back from.
        """
        process = cast_('any_', self.process)

        for line in iter(process.stdout.readline, b''):
            text = line.decode('utf8', errors='replace').rstrip()
            print(f'[HAPROXY] {text}')

# ################################################################################################################################

    def _build_environment(self) -> 'dict':
        """ The configuration reads every port and password it is not told outright from the
        environment, the same way the container's entry point supplies them. Only the MLLP port
        matters to the tests - the rest are there because the file will not parse without them.
        """
        out = os.environ.copy()

        out['Zato_Port_MLLP'] = str(self.ports.mllp_plain)
        out[Env_Port_Name] = str(self.mllp_internal_port)
        out['Zato_Port_Server'] = str(find_free_port())
        out['Zato_Port_Dashboard'] = str(find_free_port())
        out['Zato_Port_OpenAPI_Console'] = str(find_free_port())
        out['Zato_Port_Load_Balancer'] = str(find_free_port())
        out['Zato_Load_Balancer_Stats_Password'] = CryptoManager.generate_hex_string(_Password_Bits)
        out['Zato_Load_Balancer_Metrics_Password'] = CryptoManager.generate_hex_string(_Password_Bits)

        return out

# ################################################################################################################################

    def start(self) -> 'None':
        """ Runs HAProxy in the foreground and waits for both MLLP ports to accept a connection.
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
            # with whatever it printed already in the test's output
            if self.process.poll() is not None:
                raise Exception(f'HAProxy exited with code {self.process.returncode} before it bound its ports')

            if _is_port_open(self.ports.mllp_plain):
                if _is_port_open(self.ports.mllp_tls):
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

def start_haproxy(directory:'str', mllp_internal_port:'int', certificates:'TestCertificates') -> 'HAProxyHandle':
    """ Renders the configuration for one test run and starts HAProxy on it. The internal port is
    where the server's own MLLP listener sits, which is what the backend forwards to.
    """
    config_path = os.path.join(directory, 'haproxy.cfg')
    blocked_paths_path = os.path.join(directory, 'blocked-paths.txt')

    # The configuration turns away requests whose path is in this file, and HAProxy refuses to
    # start when a file an ACL names is missing, so an empty one stands in for the container's
    with open(blocked_paths_path, 'w') as blocked_paths_file:
        _ = blocked_paths_file.write('')

    ports = HAProxyPorts(
        mllp_plain=find_free_port(),
        mllp_tls=find_free_port(),
    )

    _render_config(config_path, blocked_paths_path, ports, certificates)

    out = HAProxyHandle(ports, config_path, mllp_internal_port)
    out.start()

    return out

# ################################################################################################################################
# ################################################################################################################################
