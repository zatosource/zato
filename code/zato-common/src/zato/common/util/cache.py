# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Requests
import requests
from requests import Session as RequestsSession

# Zato
from zato.common import CACHE
from zato.common.crypto import ServerCryptoManager
from zato.common.util import get_config, get_odb_session_from_server_config, get_repo_dir_from_component_dir
from zato.common.odb.model import Cluster, HTTPBasicAuth, Server

# ################################################################################################################################
# ################################################################################################################################

class CommandConfig(object):
    __slots__ = 'command', 'key', 'modifier', 'is_string_key', 'is_int_key', 'is_string_value', 'is_int_value', 'format'

    def __init__(self):
        self.command = None         # type: str
        self.key = None             # type: str
        self.modifier = None        # type: str
        self.is_string_key = None   # type: bool
        self.is_int_key = None      # type: bool
        self.is_string_value = None # type: bool
        self.is_int_value = None    # type: bool
        self.format = None          # type: str

    def to_dict(self):
        out = {}
        for name in self.__slots__:
            out[name] = getattr(self, name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class Client(object):
    """ An HTTP-based Zato cache client.
    """
    __slots__ = 'address', 'username', 'password', 'session'

    def __init__(self):
        self.address = None  # type: str
        self.username = None # type: str
        self.password = None # type: str
        self.session = None  # type: RequestsSession

# ################################################################################################################################

    @staticmethod
    def from_server_conf(server_dir):
        # type: (str) -> Client
        repo_dir = get_repo_dir_from_component_dir(server_dir)
        cm = ServerCryptoManager.from_repo_dir(None, repo_dir, None)
        secrets_conf = get_config(repo_dir, 'secrets.conf', needs_user_config=False)
        config = get_config(repo_dir, 'server.conf', crypto_manager=cm, secrets_conf=secrets_conf)

        session = None
        password = None

        try:
            session = get_odb_session_from_server_config(config, None, False)

            cluster = session.query(Server).\
                filter(Server.token == config.main.token).\
                one().cluster # type: Cluster

            security = session.query(HTTPBasicAuth).\
                filter(Cluster.id == HTTPBasicAuth.cluster_id).\
                filter(HTTPBasicAuth.username == CACHE.API_USERNAME).\
                filter(HTTPBasicAuth.cluster_id == cluster.id).\
                one() # type: HTTPBasicAuth

            password = security.password

        finally:
            if session:
                session.close()

        return Client.from_dict({
            'password': password,
            'address': config.main.gunicorn_bind
        })

# ################################################################################################################################

    @staticmethod
    def from_dict(config):
        # type: (dict) -> Client

        client = Client()
        client.username = CACHE.API_USERNAME
        client.password = config['password']
        client.address = config['address']

        session = RequestsSession()
        session.auth = (client.username, client.password)
        client.session = session

        return client

# ################################################################################################################################

    def run_command(self, command_config):
        # type: (CommandConfig)
        print(222, command_config.to_dict())

# ################################################################################################################################
# ################################################################################################################################
