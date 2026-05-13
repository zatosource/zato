# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime
from http.client import OK
from json import dumps, loads
from traceback import format_exc

# Bunch
from zato.common.ext.bunch import bunchify

# requests
import requests

# urllib3 - need for requests
from urllib3.util.retry import Retry

# Zato
from zato.common.api import URLInfo, ZATO_NOT_GIVEN
from zato.common.const import ServiceConst
from zato.common.exception import ZatoException
from zato.common.odb.model import Server
from zato.common.util.config import get_url_protocol_from_config_item

CID_LENGTH = 24

CID_NO_CLIP = int(CID_LENGTH / 2)

DEFAULT_MAX_RESPONSE_REPR = 2500
DEFAULT_MAX_CID_REPR = 5

mod_logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strtuple
    strtuple = strtuple

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
# ################################################################################################################################

class _APIResponse:
    """ Represents data returned by API services.
    """
    def __init__(self, inner, to_bunch=False, _OK=OK):
        self.inner = inner
        self.ok = inner.status_code == _OK
        self.cid = inner.headers.get('x-zato-cid', '(None)')
        self.response_time = inner.headers.get('x-response-time', '(No response time)')
        self.headers = inner.headers
        self.has_data = False
        self.meta = {}
        self.details = None
        self.data = None
        self.inner_service_response = None

        if self.ok:
            try:
                raw_data = loads(inner.text)
            except ValueError:
                raw_data = inner.text

            mod_logger.info('_APIResponse raw_data type=%s, text=%r', type(raw_data).__name__, inner.text)

            if to_bunch and isinstance(raw_data, (dict, list)):
                self.data = bunchify(raw_data)
            else:
                self.data = raw_data

            self.has_data = bool(self.data)
            self.inner_service_response = inner.text

        else:
            self.details = inner.text
            mod_logger.info('_APIResponse NOT ok, status=%s, details=%r', inner.status_code, inner.text)

    def __repr__(self):
        cid = '[{}]'.format(self.cid)
        return '<{} at {} ok:[{}] inner.status_code:[{}] cid:{}>'.format(
            self.__class__.__name__, hex(id(self)), self.ok, self.inner.status_code, cid)

    def __iter__(self):
        if isinstance(self.data, list):
            return iter(self.data)
        return iter([])

# ################################################################################################################################
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
# ################################################################################################################################

class ZatoClient:
    """ Client for invoking Zato services directly via HTTP, without the Invoke intermediary.
    """
    def __init__(self, address, path, auth=None, session=None, to_bunch=False,
                 max_response_repr=DEFAULT_MAX_RESPONSE_REPR, max_cid_repr=DEFAULT_MAX_CID_REPR, logger=None,
                 tls_verify=True):

        self.address = address
        self.path = path

        self.auth     = auth    # type: strtuple
        self.username = auth[0] # type: str
        self.password = auth[1] # type: str

        self.to_bunch = to_bunch
        self.max_response_repr = max_response_repr
        self.max_cid_repr = max_cid_repr
        self.logger = logger or mod_logger
        self.tls_verify = tls_verify
        self.has_debug = self.logger.isEnabledFor(logging.DEBUG)

        self.cluster_id = None
        self.odb_session = None

        self.session = session or requests.session()

        for adapter in self.session.adapters.values():
            retry = Retry(connect=4, backoff_factor=0.1)
            adapter.max_retries = retry

        if not self.session.auth:
            self.session.auth = auth

# ################################################################################################################################

    def set_address(self, url:'URLInfo') -> 'None':
        protocol = get_url_protocol_from_config_item(url.use_tls)
        address = f'{protocol}://{url.host}:{url.port}'
        self.address = address
        self.session = requests.session()

# ################################################################################################################################

    def _post(self, service_name, payload, headers=None):
        url_path = self.path.format(service_name)
        full_address = '{}{}'.format(self.address, url_path)
        data = dumps(payload, default=default_json_handler) if payload else None

        self.logger.info('ZatoClient._post url=%s, payload_type=%s', full_address, type(payload).__name__)

        raw_response = self.session.post(full_address, data=data, headers=headers, verify=self.tls_verify)

        self.logger.info('ZatoClient._post status=%s, text=%r', raw_response.status_code, raw_response.text)

        response = _APIResponse(raw_response, self.to_bunch)

        return response

# ################################################################################################################################

    def invoke(self, name, payload=None, headers=None, **kwargs):
        """ Invoke a service by name.
        """
        if not name:
            raise ZatoException(msg='Service name must be provided')

        extra_headers = headers or {}
        return self._post(name, payload, headers=extra_headers)

# ################################################################################################################################

    def invoke_async(self, name, payload=None, headers=None, **kwargs):
        """ Async invocation - sets the X-Zato-Async header.
        """
        extra_headers = headers or {}
        extra_headers['X-Zato-Async'] = 'true'
        return self._post(name, payload, headers=extra_headers)

# ################################################################################################################################
# ################################################################################################################################

def get_client_from_credentials(use_tls:'bool', server_url:'str', client_auth:'tuple') -> 'ZatoClient':
    api_protocol = get_url_protocol_from_config_item(use_tls)
    address = f'{api_protocol}://{server_url}'
    return ZatoClient(address, ServiceConst.API_Invoke_Url_Path, client_auth, max_response_repr=15000)

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
    """ Returns a Zato client built out of data found in a given server's config files.
    """
    # stdlib
    import os

    # To avoid circular references
    from zato.common.crypto.api import ServerCryptoManager
    from zato.common.ext.configobj_ import ConfigObj
    from zato.common.util.api import get_odb_session_from_server_config, get_repo_dir_from_component_dir
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

    # Note that we cannot use 0.0.0.0 under Windows but, since it implies localhost, we can just replace it as below.
    server_url = server_url if server_url else config.main.bind # type: str
    server_url = server_url.replace('0.0.0.0', '127.0.0.1')

    client_auth = client_auth_func(config, repo_location, crypto_manager, False, url_path=url_path)

    use_tls = config.crypto.use_tls
    api_protocol = get_url_protocol_from_config_item(use_tls)
    address = f'{api_protocol}://{server_url}'

    client = ZatoClient(address, ServiceConst.API_Invoke_Url_Path,
        client_auth, max_response_repr=15000)
    session = get_odb_session_from_server_config(config, None, False)

    client.cluster_id = session.query(Server).\
        filter(Server.token == config.main.token).\
        one().cluster_id

    client.odb_session = session

    return client

# ################################################################################################################################
# ################################################################################################################################
