# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Requests
from requests import Session as RequestsSession

# Zato
from zato.common.api import CACHE, NotGiven
from zato.common.crypto.api import ServerCryptoManager
from zato.common.json_internal import dumps
from zato.common.util.api import as_bool, get_config, get_odb_session_from_server_dir, get_repo_dir_from_component_dir
from zato.common.odb.model import Cluster, HTTPBasicAuth, Server

# ################################################################################################################################

if 0:
    from requests import Response as RequestsResponse

    RequestsResponse = RequestsResponse

# ################################################################################################################################

# Maps cache operations to HTTP verbos
op_verb_map = {
    'get': 'GET',
    'set': 'POST',
    'delete': 'DELETE'
}

# ################################################################################################################################
# ################################################################################################################################

class CommandConfig(object):
    __slots__ = 'command', 'modifier', 'key', 'value', 'is_string_key', 'is_int_key', 'is_string_value', 'is_int_value', \
        'is_bool_value', 'format'

    def __init__(self):
        self.command = None         # type: str
        self.modifier = None        # type: str
        self.key = None             # type: str
        self.value = None           # type: str
        self.is_string_key = None   # type: bool
        self.is_int_key = None      # type: bool
        self.is_string_value = None # type: bool
        self.is_int_value = None    # type: bool
        self.is_bool_value = None   # type: bool
        self.format = None          # type: str

    def to_dict(self):
        out = {}
        for name in self.__slots__:
            out[name] = getattr(self, name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class CommandResponse(object):
    __slots__ = 'key', 'text', 'has_value'

    def __init__(self):
        self.key = None       # type: object
        self.text = None      # type: str
        self.has_value = None # type: bool

# ################################################################################################################################
# ################################################################################################################################

class Client(object):
    """ An HTTP-based Zato cache client.
    """
    __slots__ = 'address', 'username', 'password', 'cache_name', 'session'

    def __init__(self):
        self.address = None    # type: str
        self.username = None   # type: str
        self.password = None   # type: str
        self.cache_name = None # type: str
        self.session = None    # type: RequestsSession

# ################################################################################################################################

    @staticmethod
    def from_server_conf(server_dir, cache_name, is_https):
        # type: (str, str, bool) -> Client
        repo_dir = get_repo_dir_from_component_dir(server_dir)
        cm = ServerCryptoManager.from_repo_dir(None, repo_dir, None)
        secrets_conf = get_config(repo_dir, 'secrets.conf', needs_user_config=False)
        config = get_config(repo_dir, 'server.conf', crypto_manager=cm, secrets_conf=secrets_conf)

        session = None
        password = None

        try:
            session = get_odb_session_from_server_dir(server_dir)

            cluster = session.query(Server).\
                filter(Server.token == config.main.token).\
                one().cluster # type: Cluster

            security = session.query(HTTPBasicAuth).\
                filter(Cluster.id == HTTPBasicAuth.cluster_id).\
                filter(HTTPBasicAuth.username == CACHE.API_USERNAME).\
                filter(HTTPBasicAuth.cluster_id == cluster.id).\
                first() # type: HTTPBasicAuth

            if security:
                password = security.password

        finally:
            if session:
                session.close()

        return Client.from_dict({
            'username': CACHE.API_USERNAME,
            'password': password,
            'address': config.main.gunicorn_bind,
            'cache_name': cache_name,
            'is_https': is_https,
        })

# ################################################################################################################################

    @staticmethod
    def from_dict(config):
        # type: (dict) -> Client

        client = Client()
        client.username = config['username']
        client.password = config['password']
        client.cache_name = config['cache_name']

        if config['address'].startswith('http'):
            address = config['address']
        else:
            address = 'http{}://{}'.format('s' if config['is_https'] else '', config['address'])

        client.address = address

        session = RequestsSession()
        if client.password:
            session.auth = (client.username, client.password)
        client.session = session

        return client

# ################################################################################################################################

    def _request(self, op, key, value=NotGiven, pattern='/zato/cache/{}', op_verb_map=op_verb_map):
        # type: (str, str, str) -> str

        # Build a full address
        path = pattern.format(key)
        address = '{}{}'.format(self.address, path)

        # Get the HTTP verb to use in the request
        verb = op_verb_map[op] # type: str

        data = {
            'cache': self.cache_name,
            'return_prev': True
        }

        if value is not NotGiven:
            data['value'] = value

        data = dumps(data)

        response = self.session.request(verb, address, data=data) # type: RequestsResponse
        return response.text

# ################################################################################################################################

    def run_command(self, config):
        # type: (CommandConfig) -> CommandResponse

        if config.value is not NotGiven:
            if config.is_int_value:
                value = int(config.value)
            elif config.is_bool_value:
                value = as_bool(config.value)
            else:
                value = config.value
        else:
            value = config.value

        raw_response = self._request(config.command, config.key, value)

        _response = CommandResponse()
        _response.key = config.key
        _response.text = raw_response

        return _response

# ################################################################################################################################
# ################################################################################################################################
