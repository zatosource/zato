# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from base64 import b64decode, b64encode
from datetime import datetime
from http.client import OK
from json import dumps, loads
from traceback import format_exc

# Bunch
from bunch import bunchify

# requests
import requests

# urllib3 - need for requests
from urllib3.util.retry import Retry

# Python 2/3 compatibility
from builtins import str as text
from six import PY3

# Zato
from zato.common.api import BROKER, URLInfo, ZATO_NOT_GIVEN, ZATO_OK
from zato.common.const import ServiceConst
from zato.common.exception import ZatoException
from zato.common.log_message import CID_LENGTH
from zato.common.odb.model import Server
from zato.common.util.config import get_url_protocol_from_config_item

# Set max_cid_repr to CID_NO_CLIP if it's desired to return the whole of a CID
# in a response's __repr__ method.
CID_NO_CLIP = int(CID_LENGTH / 2)

DEFAULT_MAX_RESPONSE_REPR = 2500
DEFAULT_MAX_CID_REPR = 5

mod_logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strtuple

# ################################################################################################################################
# Version
# ################################################################################################################################

version = '3.2.1'

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
        self.is_ok = self.inner.status_code == _OK
        self.cid = self.inner.headers.get('x-zato-cid', '(None)')
        self.response_time = self.inner.headers.get('x-response-time', '(No response time)')
        self.headers = self.inner.headers

        if self.is_ok:
            self.data = loads(self.inner.text)
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

# Clients below are preserved only for compatibility with pre-3.0 environments and will be removed at one point

# ################################################################################################################################
# ################################################################################################################################

class _Response:
    """ A base class for all specific response types client may return.
    """
    def __init__(self, inner, to_bunch, max_response_repr, max_cid_repr, logger, output_repeated=False):
        self.inner = inner # Acutal response from the requests module
        self.to_bunch = to_bunch
        self.max_response_repr = max_response_repr
        self.max_cid_repr = max_cid_repr
        self.logger = logger
        self.sio_result = None
        self.ok = False
        self.has_data = False
        self.output_repeated = output_repeated
        self.data = [] if self.output_repeated else None
        self.meta = {}
        self.cid = self.inner.headers.get('x-zato-cid', '(None)')
        self.response_time = self.inner.headers.get('x-response-time', '(No response time)')
        self.details = None
        self.init()

    def __repr__(self):
        if self.max_cid_repr >= CID_NO_CLIP:
            cid = '[{}]'.format(self.cid)
        else:
            cid = '[{}..{}]'.format(self.cid[:self.max_cid_repr], self.cid[-self.max_cid_repr:])

        return '<{} at {} ok:[{}] inner.status_code:[{}] cid:{}, inner.text:[{}]>'.format(
            self.__class__.__name__, hex(id(self)), self.ok, self.inner.status_code,
            cid, self.inner.text[:self.max_response_repr])

    def __iter__(self):
        return iter(self.data)

    def init(self):
        raise NotImplementedError('Must be defined by subclasses')

# ################################################################################################################################

class _StructuredResponse(_Response):
    """ Any non-raw and non-SIO response.
    """
    def init(self):
        if self.set_data():
            self.set_has_data()
            self.set_ok()

    def _set_data_details(self):
        try:
            self.data = self.load_func(self.inner.text.encode('utf-8'))
        except Exception:
            self.details = format_exc()
        else:
            return True

    def load_func(self):
        raise NotImplementedError('Must be defined by subclasses')

    def set_data(self):
        return self._set_data_details()

    def set_has_data(self):
        raise NotImplementedError('Must be defined by subclasses')

    def set_ok(self):
        self.ok = self.inner.ok

class JSONResponse(_StructuredResponse):
    """ Stores responses from JSON services.
    """
    def load_func(self, data):
        return loads(data)

    def set_has_data(self):
        self.has_data = bool(self.data)

# ################################################################################################################################

class JSONSIOResponse(_Response):
    """ Stores responses from JSON SIO services.
    """
    def init(self, _non_data=('zato_env', '_meta')):
        try:
            json = loads(self.inner.text)
        except ValueError:
            msg = 'inner.status_code `{}`, JSON parsing error `{}`'.format(self.inner.status_code, self.inner.text)
            self.logger.error(msg)
            raise ValueError(msg)

        if 'zato_env' in json:
            has_zato_env = True
            self.details = json['zato_env']['details']
            self.sio_result = json['zato_env']['result']
            self.ok = self.sio_result == ZATO_OK
        else:
            has_zato_env = False
            self.details = self.inner.text
            self.ok = self.inner.ok

        if self.ok:
            value = None

            if has_zato_env:
                # There will be two keys, zato_env and the actual payload
                for key, _value in json.items():
                    if key not in _non_data:
                        value = _value
                        break
            else:
                value = json

            if value:
                if self.set_data(value, has_zato_env):
                    self.has_data = True
                    if self.to_bunch:
                        self.data = bunchify(self.data)

    def set_data(self, payload, _ignored):
        self.data = payload
        return True

class ServiceInvokeResponse(JSONSIOResponse):
    """ Stores responses from SIO services invoked through the zato.service.invoke service.
    """
    def __init__(self, *args, **kwargs):
        self.inner_service_response = None
        super(ServiceInvokeResponse, self).__init__(*args, **kwargs)

    def _handle_response_with_meta(self, data):

        if isinstance(data, dict):
            self.meta = data.get('_meta')
            data_keys = list(data.keys())
            if len(data_keys) == 1:
                data_key = data_keys[0]
                if isinstance(data_key, text) and data_key.startswith('zato'):
                    self.data = data[data_key]
                else:
                    self.data = data
            else:
                self.data = data
        else:
            self.data = data

    def set_data(self, payload, has_zato_env):

        if has_zato_env:
            payload = b64decode(payload)
            payload = payload.decode('utf8') if isinstance(payload, bytes) else payload
            self.inner_service_response = payload

            try:
                data = loads(self.inner_service_response)
            except ValueError:
                # Not a JSON response
                self.data = self.inner_service_response
            else:
                self._handle_response_with_meta(data)
        else:
            try:
                data = loads(payload)
            except ValueError:
                # Not a JSON response
                self.data = payload
            else:
                self._handle_response_with_meta(data)

        return True

# ################################################################################################################################

class RawDataResponse(_Response):
    """ Stores responses from services that weren't invoked using any particular
    data format
    """
    def init(self):
        self.ok = self.inner.ok
        if self.set_data():
            self.has_data = True

    def set_data(self):
        if self.ok:
            self.data = self.inner.text
        else:
            self.details = self.inner.text

        return self.data and len(self.data) > 0

# ################################################################################################################################

class _Client:
    """ A base class of convenience clients for invoking Zato services from other Python applications.
    """

    service_address: 'str'
    session: 'any_'

    def __init__(self, address, path, auth=None, session=None, to_bunch=False,
                 max_response_repr=DEFAULT_MAX_RESPONSE_REPR, max_cid_repr=DEFAULT_MAX_CID_REPR, logger=None,
                 tls_verify=True):

        self.address = address
        self.path = path

        self.auth     = auth    # type: strtuple
        self.username = auth[0] # type: str
        self.password = auth[1] # type: str

        self.set_service_address()
        self.set_session(session)

        for adapter in self.session.adapters.values():
            retry = Retry(connect=4, backoff_factor=0.1)
            adapter.max_retries = retry

        self.to_bunch = to_bunch
        self.max_response_repr = max_response_repr
        self.max_cid_repr = max_cid_repr
        self.logger = logger or mod_logger
        self.tls_verify = tls_verify
        self.has_debug = self.logger.isEnabledFor(logging.DEBUG)

        if not self.session.auth:
            self.session.auth = auth

# ################################################################################################################################

    def inner_invoke(self, request, response_class, is_async, headers, output_repeated=False):
        """ Actually invokes a service through HTTP and returns its response.
        """
        raw_response = self.session.post(self.service_address, request, headers=headers, verify=self.tls_verify)
        response = response_class(
            raw_response, self.to_bunch, self.max_response_repr,
            self.max_cid_repr, self.logger, output_repeated)

        if isinstance(request, (bytes, bytearray)):
            request = request.decode('utf-8')

        if self.has_debug:
            msg = 'request:[%s]\nresponse_class:[%s]\nis_async:[%s]\nheaders:[%s]\n text:[%s]\ndata:[%s]'
            self.logger.debug(msg, request, response_class, is_async, headers, raw_response.text, response.data)

        return response

# ################################################################################################################################

    def invoke(self, request, response_class, is_async=False, headers=None, output_repeated=False):
        """ Input parameters are like when invoking a service directly.
        """
        headers = headers or {}
        return self.inner_invoke(request, response_class, is_async, headers)

# ################################################################################################################################

    def set_service_address(self):
        self.service_address = '{}{}'.format(self.address, self.path)

# ################################################################################################################################

    def set_address(self, url:'URLInfo') -> 'None':

        # Extract details from the URL ..
        protocol = get_url_protocol_from_config_item(url.use_tls)

        # .. build a new address ..
        address = f'{protocol}://{url.host}:{url.port}'

        # .. set it for later use ..
        self.address = address

        # .. and rebuild the underlying configuration.
        self.set_service_address()
        self.set_session(None)

# ################################################################################################################################

    def set_session(self, session:'any_') -> 'None':
        self.session = session or requests.session()

# ################################################################################################################################
# ################################################################################################################################

class _JSONClient(_Client):
    """ Base class for all JSON clients.
    """
    response_class = None

    def invoke(self, payload='', headers=None, to_json=True):
        if to_json:
            payload = dumps(payload, default=default_json_handler)
        return super(_JSONClient, self).invoke(payload, self.response_class, headers=headers)

class JSONClient(_JSONClient):
    """ Client for services that accept JSON input.
    """
    response_class = JSONResponse

# ################################################################################################################################

class JSONSIOClient(_JSONClient):
    """ Client for services that accept Simple IO (SIO) in JSON.
    """
    response_class = JSONSIOResponse

class AnyServiceInvoker(_Client):
    """ Uses zato.service.invoke to invoke other services. The services being invoked
    don't have to be available through any channels, it suffices for zato.service.invoke
    to be exposed over HTTP.
    """
    def _invoke(self, name=None, payload='', headers=None, channel='invoke', data_format='json',
                transport=None, is_async=False, expiration=BROKER.DEFAULT_EXPIRATION, id=None,
                to_json=True, output_repeated=ZATO_NOT_GIVEN, pid=None, all_pids=False, timeout=None,
                skip_response_elem=True, needs_response_time=True, **kwargs):

        if not(name or id):
            raise ZatoException(msg='Either name or id must be provided')

        if name and output_repeated == ZATO_NOT_GIVEN:
            output_repeated = name.lower().endswith('list')

        if to_json:
            payload = dumps(payload, default=default_json_handler)

        id_, value = ('name', name) if name else ('id', id)

        request = {
            id_: value,
            'payload': b64encode(payload.encode('utf8') if PY3 else payload),
            'channel': channel,
            'data_format': data_format,
            'transport': transport,
            'is_async': is_async,
            'expiration':expiration,
            'pid':pid,
            'all_pids': all_pids,
            'timeout': timeout,
            'skip_response_elem': skip_response_elem,
            'needs_response_time': needs_response_time,
            'needs_headers': True,
        }

        return super(AnyServiceInvoker, self).invoke(dumps(request, default=default_json_handler),
            ServiceInvokeResponse, is_async, headers, output_repeated)

    def invoke(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._invoke(is_async=False, *args, **kwargs)

    def invoke_async(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._invoke(is_async=True, *args, **kwargs)

# ################################################################################################################################

class RawDataClient(_Client):
    """ Client which doesn't process requests before passing them into a service.
    Likewise, no parsing of response is performed.
    """
    def invoke(self, payload='', headers=None):
        return super(RawDataClient, self).invoke(payload, RawDataResponse, headers=headers)

# ################################################################################################################################

class ZatoClient(AnyServiceInvoker):
    def __init__(self, *args, **kwargs):
        super(ZatoClient, self).__init__(*args, **kwargs)
        self.cluster_id = None
        self.odb_session = None

# ################################################################################################################################

def get_client_from_credentials(use_tls:'bool', server_url:'str', client_auth:'tuple') -> 'ZatoClient':
    api_protocol = get_url_protocol_from_config_item(use_tls)
    address = f'{api_protocol}://{server_url}'
    return ZatoClient(address, ServiceConst.API_Admin_Invoke_Url_Path, client_auth, max_response_repr=15000)

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
    server_url = server_url if server_url else config.main.gunicorn_bind # type: str
    server_url = server_url.replace('0.0.0.0', '127.0.0.1')

    client_auth = client_auth_func(config, repo_location, crypto_manager, False, url_path=url_path)

    use_tls = config.crypto.use_tls
    api_protocol = get_url_protocol_from_config_item(use_tls)
    address = f'{api_protocol}://{server_url}'

    client = ZatoClient(address, ServiceConst.API_Admin_Invoke_Url_Path,
        client_auth, max_response_repr=15000)
    session = get_odb_session_from_server_config(config, None, False)

    client.cluster_id = session.query(Server).\
        filter(Server.token == config.main.token).\
        one().cluster_id

    client.odb_session = session

    return client

# ################################################################################################################################
# ################################################################################################################################
