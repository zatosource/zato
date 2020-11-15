# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import errno
import socket
from datetime import datetime, timedelta
from logging import getLogger
from time import sleep

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

def get_free_port(start=30000):
    port = start
    while is_port_taken(port):
        port += 1
    return port

# ################################################################################################################################

# Taken from http://grodola.blogspot.com/2014/04/reimplementing-netstat-in-cpython.html
def is_port_taken(port):

    # stdlib
    from platform import system as platform_system

    # psutil
    import psutil

    is_linux=platform_system().lower()=='linux'

    # Short for Linux so as not to bind to a socket which in turn means waiting until it's closed by OS
    if is_linux:
        for conn in psutil.net_connections(kind='tcp'):
            if conn.laddr[1] == port and conn.status == psutil.CONN_LISTEN:
                return True
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', port))
            sock.close()
        except socket.error as e:
            if e.args[0] == errno.EADDRINUSE:
                return True
            raise

# ################################################################################################################################

def _is_port_ready(port, needs_taken):
    taken = is_port_taken(port)
    return taken if needs_taken else not taken

# ################################################################################################################################

def _wait_for_port(port, timeout, interval, needs_taken):
    port_ready = _is_port_ready(port, needs_taken)

    if not port_ready:
        start = datetime.utcnow()
        wait_until = start + timedelta(seconds=timeout)

        while not port_ready:
            sleep(interval)
            port_ready = _is_port_ready(port, needs_taken)
            if datetime.utcnow() > wait_until:
                break

    return port_ready

# ################################################################################################################################

def wait_for_zato(address, url_path, timeout=60, interval=0.1):
    """ Waits until a Zato server responds.
    """

    # Requests
    from requests import get as requests_get

    # Imported here to avoid circular imports
    from zato.common.util.api import wait_for_predicate

    # Full URL to check a Zato server under
    url = address + url_path

    def _predicate_zato_ping(*ignored_args, **ignored_kwargs):
        try:
            requests_get(url, timeout=interval)
        except Exception as e:
            logger.warn('Waiting for `%s` (%s)', url, e)
        else:
            return True

    return wait_for_predicate(_predicate_zato_ping, timeout, interval, address)

# ################################################################################################################################

def wait_for_zato_ping(address, timeout=60, interval=0.1):
    """ Waits for timeout seconds until address replies to a request sent to /zato/ping.
    """
    wait_for_zato(address, '/zato/ping', timeout, interval)

# ################################################################################################################################

def wait_until_port_taken(port, timeout=2, interval=0.1):
    """ Waits until a given TCP port becomes taken, i.e. a process binds to a TCP socket.
    """
    return _wait_for_port(port, timeout, interval, True)

# ################################################################################################################################

def wait_until_port_free(port, timeout=2, interval=0.1):
    """ Waits until a given TCP port becomes free, i.e. a process releases a TCP socket.
    """
    return _wait_for_port(port, timeout, interval, False)

# ################################################################################################################################
