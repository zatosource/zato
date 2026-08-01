# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import socket
import subprocess
import threading
import time

# Zato
from hl7_client.java_build import build_project, get_launcher_path, is_java_available
from hl7_client.mllp_receiver import ReceivedDelivery
from hl7_client.ports import find_free_port
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from hl7_client.mllp_receiver import delivery_list
    from zato.common.typing_ import any_

    any_ = any_
    delivery_list = delivery_list
    Popen = Popen

# ################################################################################################################################
# ################################################################################################################################

# What the listener's Gradle project is called, which is also what its launcher is named after
_Project_Name = 'hl7-mllp-server'

# What the listener binds to, the same loopback address every other test listener uses
_Host = '127.0.0.1'

# The lines the listener writes that mean something here
_Ready_Prefix    = 'READY:'
_Received_Prefix = 'RECEIVED:'

# How long the listener is given to bind its port and say so
_Ready_Timeout = 60

# How often its output is checked while waiting for that
_Ready_Poll_Interval = 0.1

# How long it is given to end once it has been asked to
_Shutdown_Timeout = 10

# How long a check of whether the port is bound waits for the connection
_Port_Check_Timeout = 1.0

# The system property HAPI's own lower layer reads the character set of the wire out of
_Charset_Property = 'ca.uhn.hl7v2.llp.charset'

# The check for a Java runtime is the same one every Java-backed helper here makes, and it is
# re-exported so that a caller of this module has no second module to import for it
is_java_available = is_java_available

# ################################################################################################################################
# ################################################################################################################################

def build_receiver() -> 'None':
    """ Builds the HAPI listener with Gradle, unless what is already installed is newer than its
    sources. The first build downloads the HAPI dependencies from Maven Central.
    """
    _ = build_project(_Project_Name)

# ################################################################################################################################
# ################################################################################################################################

class JavaMLLPReceiver:
    """ HAPI's own MLLP listener, the reference implementation of the receiving side, run as a
    process of its own and reporting every message it takes. It offers the same handful of things
    the hl7apy receiver offers - a port that survives a stop and a start, a record of what arrived
    and a configurable amount of time taken over each message - so that one test can be pointed at
    either of them without knowing which it got.
    """

    def __init__(
        self,
        delay:'float'=0.0,
        ack_code:'str'='AA',
        is_never_answering:'bool'=False,
        keystore_path:'str'='',
        keystore_password:'str'='',
    ) -> 'None':

        self.delay = delay
        self.ack_code = ack_code
        self.is_never_answering = is_never_answering

        # A key store makes the listener terminate TLS, which is what an outgoing connection with
        # a CA bundle configured expects to find at the other end
        self.keystore_path = keystore_path
        self.keystore_password = keystore_password

        self.port = find_free_port()

        self.deliveries:'delivery_list' = []

        # Nothing here answers a message it does not handle, HAPI taking every message type there
        # is, so this stays empty and exists only because the hl7apy receiver has one
        self.unexpected:'delivery_list' = []

        self._process:'subprocess.Popen[bytes] | None' = None
        self._is_ready = threading.Event()

# ################################################################################################################################

    def _build_command(self) -> 'list[str]':
        """ Builds the command line the listener is started with.
        """
        launcher_path = get_launcher_path(_Project_Name)

        # The delay reaches the listener in milliseconds, which is the unit it takes and the one
        # everything else about an MLLP timeout is expressed in
        delay_ms = int(self.delay * 1000)

        out = [
            launcher_path,
            '--port', str(self.port),
            '--ack-code', self.ack_code,
            '--delay-ms', str(delay_ms),
            '--tls', 'true' if self.keystore_path else 'false',
            '--never-answer', 'true' if self.is_never_answering else 'false',
        ]

        return out

# ################################################################################################################################

    def _build_environment(self) -> 'dict[str, str]':
        """ Builds the environment the listener runs in. TLS is the JVM's own, so what the listener
        presents is named through the standard system properties rather than on its command line.
        """
        out = os.environ.copy()

        # HAPI reads a frame off the wire in whichever character set its lower layer was configured
        # for, and left to itself that is the machine's own rather than the message's. Everything
        # Zato sends is UTF-8, so this is the receiving system configured to match its sender - the
        # same setting a real deployment has to make, and without it every name outside ASCII
        # arrives as a run of replacement characters.
        java_options = [f'-D{_Charset_Property}=UTF-8']

        if self.keystore_path:
            java_options.append(f'-Djavax.net.ssl.keyStore={self.keystore_path}')
            java_options.append(f'-Djavax.net.ssl.keyStorePassword={self.keystore_password}')
            java_options.append('-Djavax.net.ssl.keyStoreType=PKCS12')

        out['JAVA_OPTS'] = ' '.join(java_options)

        return out

# ################################################################################################################################

    def _read_output(self) -> 'None':
        """ Drains what the listener writes, which is both how a full pipe never blocks it and how
        every message it took reaches this process.
        """
        process = cast_('Popen', self._process)
        output = cast_('any_', process.stdout)

        for line in iter(output.readline, b''):

            text = line.decode('utf8', errors='replace').rstrip()

            if text.startswith(_Ready_Prefix):
                self._is_ready.set()
                continue

            if text.startswith(_Received_Prefix):

                # The listener writes one message per line with its separators escaped, so that
                # two senders at once cannot produce a line neither of them sent
                escaped = text[len(_Received_Prefix):]
                message = escaped.replace('\\r', '\r').replace('\\n', '\n')

                now = time.monotonic()
                self.deliveries.append(ReceivedDelivery(message, now, now))
                continue

            print(f'[HAPI RECEIVER] {text}')

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the listener and returns once it is taking connections. Its port stays the same
        across a stop and a start, the way a real system comes back on the address its senders know.
        """
        build_receiver()

        self._is_ready.clear()

        # A new session makes the listener its own process group leader, so a stop can end the
        # whole of it - the launcher's shell wrapper and the JVM it started included
        self._process = subprocess.Popen(
            self._build_command(),
            env=self._build_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        output_thread = threading.Thread(target=self._read_output, daemon=True)
        output_thread.start()

        deadline = time.monotonic() + _Ready_Timeout

        while time.monotonic() < deadline:

            # HAPI reports its listener as running from the moment the thread behind it starts,
            # which is before that thread has bound anything, so the port itself is what decides
            # whether a sender pointed here now would get through
            if self._is_ready.is_set():
                if self._is_port_open():
                    return

            # A listener that gave up leaves nothing to wait for, and whatever it printed
            # on its way out is already in this run's output
            if self._process.poll() is not None:
                raise Exception(f'The HAPI listener exited with code {self._process.returncode} before it was ready')

            time.sleep(_Ready_Poll_Interval)

        self.stop()
        raise Exception(f'The HAPI listener did not bind port {self.port} within {_Ready_Timeout}s')

# ################################################################################################################################

    def _is_port_open(self) -> 'bool':
        """ Returns whether the listener's port takes a connection. The connection is closed again
        right away, which for a listener terminating TLS is a handshake that never begins - it
        costs the listener a discarded connection and tells this side what it needs to know.
        """
        probe_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe_socket.settimeout(_Port_Check_Timeout)

        try:
            probe_socket.connect((_Host, self.port))
            out = True
        except OSError:
            out = False
        finally:
            probe_socket.close()

        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Ends the listener, leaving its port free for a later start.
        """
        process = self._process

        if process is None:
            return

        if process.poll() is None:

            # The launcher is a shell wrapper around the JVM, so ending the direct child alone
            # would leave the listener itself running and holding the port. The process is its
            # own group leader, which makes the whole group what has to be ended.
            group_id = os.getpgid(process.pid)
            os.killpg(group_id, signal.SIGTERM)

            try:
                _ = process.wait(timeout=_Shutdown_Timeout)
            except subprocess.TimeoutExpired:
                os.killpg(group_id, signal.SIGKILL)
                _ = process.wait(timeout=_Shutdown_Timeout)

        self._process = None

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        """ Where an outgoing connection is pointed to reach this listener.
        """
        out = f'{_Host}:{self.port}'
        return out

# ################################################################################################################################
# ################################################################################################################################
