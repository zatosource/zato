# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from http.client import HTTPConnection, OK

# Zato
from zato_deploy.common import Path

# ################################################################################################################################
# ################################################################################################################################

_Ping_Timeout = 5

# ################################################################################################################################
# ################################################################################################################################

class DockerConnection(HTTPConnection):
    """ A connection to the Docker Engine API over its Unix socket.
    """
    def __init__(self, timeout:'float | None') -> 'None':
        super().__init__('localhost', timeout=timeout)

# ################################################################################################################################

    def connect(self) -> 'None':

        docker_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        docker_socket.settimeout(self.timeout)
        docker_socket.connect(Path.Docker_Socket)

        self.sock = docker_socket

# ################################################################################################################################
# ################################################################################################################################

def is_docker_answering() -> 'bool':
    """ Returns whether the Docker daemon accepts requests.
    """
    connection = DockerConnection(_Ping_Timeout)

    try:
        connection.request('GET', '/_ping')
        response = connection.getresponse()
        _ = response.read()
        out = response.status == OK
    except OSError:
        out = False
    finally:
        connection.close()

    return out

# ################################################################################################################################
# ################################################################################################################################
