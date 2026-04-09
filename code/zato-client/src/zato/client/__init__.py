# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from http.client import OK
from json import dumps, loads

# requests
import requests

# Zato
from zato.common.util.config import get_url_protocol_from_config_item

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# Version
# ################################################################################################################################

version = '4.1'

# ################################################################################################################################
# ################################################################################################################################

def default_json_handler(value):
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, bytes):
        return value.decode('utf8')
    raise TypeError('Cannot serialize `{}`'.format(value))

# ################################################################################################################################

class _APIResponse:
    """ A class to represent data returned by API services.
    """
    def __init__(self, inner, _OK=OK):
        self.inner = inner
        self.ok = self.inner.status_code == _OK
        self.has_data = False
        self.cid = self.inner.headers.get('x-zato-cid', '(None)')
        self.response_time = self.inner.headers.get('x-response-time', '(No response time)')
        self.headers = self.inner.headers

        if self.ok:
            self.data = loads(self.inner.text)
            self.has_data = bool(self.data)
            self.details = None
        else:
            self.data = ''
            self.details = self.inner.text

# ################################################################################################################################

class APIClient:
    def __init__(self, address, username, password, path='/zato/api/invoke/{}', tls_verify=None, tls_cert=None):
        self.address = address
        self.username = username
        self.password = password
        self.path = path

        self.tls_verify = tls_verify
        self.tls_cert = tls_cert

        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.verify = self.tls_verify
        self.session.cert = self.tls_cert

    def _invoke(self, verb, service_name, request=None):
        func = getattr(self.session, verb)
        url_path = self.path.format(service_name)
        full_address = '{}{}'.format(self.address, url_path)
        response = func(full_address, verify=self.tls_verify, data=dumps(request, default=default_json_handler))

        return _APIResponse(response)

    def invoke(self, *args, **kwargs):
        return self._invoke('post', *args, **kwargs)

    def get(self, *args, **kwargs):
        return self._invoke('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._invoke('post', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._invoke('patch', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._invoke('put', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._invoke('delete', *args, **kwargs)

    def by_verb(self, verb, *args, **kwargs):
        return self._invoke(verb, *args, **kwargs)

# ################################################################################################################################

def get_client_from_credentials(use_tls:'bool', server_url:'str', client_auth:'tuple') -> 'APIClient':
    api_protocol = get_url_protocol_from_config_item(use_tls)
    address = f'{api_protocol}://{server_url}'
    return APIClient(address, client_auth[0], client_auth[1])

# ################################################################################################################################

def get_client_from_server_conf(
    server_dir,
    client_auth_func,
    get_config_func,
    server_url=None,
    stdin_data=None,
    *,
    url_path=None,
):
    """ Returns an APIClient built out of data found in a given server's config files.
    """
    # stdlib
    import os

    # To avoid circular references
    from zato.common.crypto.api import ServerCryptoManager
    from zato.common.ext.configobj_ import ConfigObj
    from zato.common.util.api import get_repo_dir_from_component_dir
    from zato.common.util.cli import read_stdin_data

    repo_location = get_repo_dir_from_component_dir(server_dir)
    stdin_data = stdin_data or read_stdin_data()
    crypto_manager = ServerCryptoManager.from_repo_dir(None, repo_location, stdin_data=stdin_data)

    secrets_config = ConfigObj(os.path.join(repo_location, 'secrets.conf'), use_zato=False)
    secrets_conf = get_config_func(
        repo_location,
        'secrets.conf',
        needs_user_config=False,
        crypto_manager=crypto_manager,
        secrets_conf=secrets_config
    )

    config = get_config_func(
        repo_location,
        'server.conf',
        crypto_manager=crypto_manager,
        secrets_conf=secrets_conf,
    )

    server_url = server_url if server_url else f'{config.main.host}:{config.main.port}' # type: str
    server_url = server_url.replace('0.0.0.0', '127.0.0.1')

    client_auth = client_auth_func(config, repo_location, crypto_manager, False, url_path=url_path)

    use_tls = config.crypto.use_tls
    api_protocol = get_url_protocol_from_config_item(use_tls)
    address = f'{api_protocol}://{server_url}'

    return APIClient(address, client_auth[0], client_auth[1])

# ################################################################################################################################
# ################################################################################################################################
