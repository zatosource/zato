# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Helpers for local server processes that a Zato process starts on 127.0.0.1 - starting one with its output
# in a log file, recognizing it later by its pid file, stopping it and finding a port for it.

# stdlib
import os
import signal
import socket
from subprocess import DEVNULL, Popen, STDOUT
from time import monotonic, sleep

# Zato
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The interface every local server listens on
Local_Host = '127.0.0.1'

# How long to wait for a server to accept connections, in seconds
Default_Start_Timeout = 15.0

# How long to wait for a stopped process to go away, in seconds
Default_Stop_Timeout = 10.0

# How long to sleep between two checks of a port or of a process, in seconds
_poll_interval = 0.1

# How long a single probe connection may take, in seconds
_connect_timeout = 1.0

# ################################################################################################################################
# ################################################################################################################################

def start_logged_process(command:'strlist', log_path:'str') -> 'Popen':
    """ Starts a process whose standard output and error go to a log file, appended to, or are discarded
    when no log file is given. Nothing reads pipes of such a process, so its output never goes to one.
    """
    if log_path:
        with open(log_path, 'ab') as log_file:
            out = Popen(command, stdin=DEVNULL, stdout=log_file, stderr=STDOUT)
    else:
        out = Popen(command, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)

    return out

# ################################################################################################################################

def read_pid_file(pid_file_path:'str') -> 'int':
    """ Returns the pid a pid file holds, zero if there is no such file or it holds no number.
    """
    if not os.path.exists(pid_file_path):
        return 0

    with open(pid_file_path, encoding='utf8') as pid_file:
        data = pid_file.read()

    data = data.strip()

    if data.isdigit():
        out = int(data)
    else:
        out = 0

    return out

# ################################################################################################################################

def write_pid_file(pid_file_path:'str', pid:'int') -> 'None':
    """ Writes a pid out to a pid file.
    """
    with open(pid_file_path, 'w', encoding='utf8') as pid_file:
        _ = pid_file.write(f'{pid}\n')

# ################################################################################################################################

def is_expected_process(pid:'int', marker:'str') -> 'bool':
    """ Whether a process of this pid is alive and its command line contains the marker,
    which is how a pid reused by an unrelated process is told apart from the expected server.
    """
    if not pid:
        return False

    cmdline_path = f'/proc/{pid}/cmdline'

    try:
        with open(cmdline_path, 'rb') as cmdline_file:
            data = cmdline_file.read()
    except OSError:
        return False

    # The arguments are separated by NUL bytes, unless the process rewrote its title into one string.
    data = data.replace(b'\x00', b' ')
    cmdline = data.decode('utf8', 'replace')

    out = marker in cmdline
    return out

# ################################################################################################################################

def stop_pid(pid:'int', marker:'str', timeout:'float'=Default_Stop_Timeout) -> 'bool':
    """ Stops the process of this pid with SIGTERM, but only if it still is the expected one,
    and waits until it goes away. Returns whether such a process was found.
    """
    if not is_expected_process(pid, marker):
        return False

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return False

    # Wait until the process is gone ..
    deadline = monotonic() + timeout

    while monotonic() < deadline:
        if not is_expected_process(pid, marker):
            break
        sleep(_poll_interval)

    # .. and if it is still there, it does not get to finish on its own terms.
    else:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    return True

# ################################################################################################################################

def stop_popen(process:'Popen', timeout:'float'=Default_Stop_Timeout) -> 'None':
    """ Stops a process this very process started, with SIGTERM first and SIGKILL if it does not end in time.
    """
    if process.poll() is not None:
        return

    process.terminate()

    try:
        _ = process.wait(timeout=timeout)
    except Exception:
        process.kill()
        _ = process.wait()

# ################################################################################################################################

def is_port_free(port:'int', host:'str'=Local_Host) -> 'bool':
    """ Whether a server could bind to this port right now. The probe binds the way servers do, so connections
    of an earlier server that are still winding down do not count, while another listener on the port still does.
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        tcp_socket.bind((host, port))
    except OSError:
        out = False
    else:
        out = True
    finally:
        tcp_socket.close()

    return out

# ################################################################################################################################

def reuse_or_pick_port(port:'int', taken:'intlist | None'=None) -> 'int':
    """ Returns the port given if a server can still bind to it, or a new free one otherwise.
    The ports in taken are never returned, which keeps several servers started together apart.
    """
    if taken is None:
        taken = []

    if port:
        if port not in taken:
            if is_port_free(port):
                return port

    out = get_free_port()

    while out in taken:
        out = get_free_port(out + 1)

    return out

# ################################################################################################################################

def is_accepting_connections(port:'int', host:'str'=Local_Host) -> 'bool':
    """ Whether something accepts TCP connections on this port right now.
    """
    try:
        with socket.create_connection((host, port), timeout=_connect_timeout):
            out = True
    except OSError:
        out = False

    return out

# ################################################################################################################################

def wait_until_accepting_connections(
    port:'int',
    host:'str' = Local_Host,
    timeout:'float' = Default_Start_Timeout,
    process:'Popen | None' = None,
    ) -> 'None':
    """ Waits until something accepts connections on this port. A process given on input that ends
    in the meantime ends the wait at once, because nothing is ever going to listen then.
    """
    deadline = monotonic() + timeout

    while monotonic() < deadline:

        if is_accepting_connections(port, host):
            return

        if process:
            if process.poll() is not None:
                raise Exception(f'Process {process.pid} exited with {process.returncode} before listening on {host}:{port}')

        sleep(_poll_interval)

    raise Exception(f'Nothing accepted connections on {host}:{port} within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################
