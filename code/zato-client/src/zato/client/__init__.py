# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, os
from datetime import datetime
from httplib import OK
from inspect import getargspec
from json import dumps, loads
from traceback import format_exc

# anyjson
from anyjson import dumps as anyjson_dumps

# Bunch
from bunch import bunchify

# lxml
from lxml import objectify

# requests
import requests

# Zato
from zato.common import BROKER, soap_data_path, soap_data_xpath, soap_fault_xpath, \
     ZatoException, zato_data_path, zato_data_xpath, zato_details_xpath, \
     ZATO_NOT_GIVEN, ZATO_OK, zato_result_xpath
from zato.common.log_message import CID_LENGTH
from zato.common.odb.model import Server

# Set max_cid_repr to CID_NO_CLIP if it's desired to return the whole of a CID
# in a response's __repr__ method.
CID_NO_CLIP = int(CID_LENGTH / 2)

DEFAULT_MAX_RESPONSE_REPR = 2500
DEFAULT_MAX_CID_REPR = 5

mod_logger = logging.getLogger(__name__)

# For pyflakes
dumps = dumps

# Work around https://bitbucket.org/runeh/anyjson/pull-request/4/
if getargspec(anyjson_dumps).keywords:
    dumps = anyjson_dumps
else:
    def dumps(data, *args, **kwargs):
        return anyjson_dumps(data)

# ################################################################################################################################
# Version
# ################################################################################################################################

version = '3.0.2'

# ################################################################################################################################
# ################################################################################################################################

class _APIResponse(object):
    """ A class to represent data returned by API services.
    """
    def __init__(self, inner, _OK=OK):
        self.inner = inner
        self.is_ok = self.inner.status_code == _OK
        self.cid = self.inner.headers.get('x-zato-cid', '(None)')

        if self.is_ok:
            self.data = loads(self.inner.text)
            self.details = None
        else:
            self.data = ''
            self.details = self.inner.text

# ################################################################################################################################

class APIClient(object):
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
        response = func(full_address, verify=self.tls_verify, data=dumps(request))

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

class _Response(object):
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
        except Exception, e:
            self.details = format_exc(e)
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

class XMLResponse(_StructuredResponse):
    """ Stores responses from XML services.
    """
    def load_func(self, data):
        return objectify.fromstring(data)

    def set_has_data(self):
        self.has_data = self.data is not None

class SOAPResponse(XMLResponse):
    """ Stores responses from SOAP services.
    """
    path, xpath = soap_data_path, soap_data_xpath

    def init(self):
        if self.set_data():
            self.set_has_data()

    def set_data(self):
        if self._set_data_details():
            data = self.xpath(self.data)
            if not data:
                self.details = 'No {} in SOAP response'.format(self.path)
            else:
                if soap_fault_xpath(data[0]):
                    self.details = data[0]
                else:
                    self.data = data[0]
                    self.ok = True
                    return True

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
            if has_zato_env:
                # There will be two keys, zato_env and the actual payload
                for key, _value in json.items():
                    if key not in _non_data:
                        value = _value
                        break
            else:
                value = json

            if self.set_data(value, has_zato_env):
                self.has_data = True
                if self.to_bunch:
                    self.data = bunchify(self.data)

    def set_data(self, payload, _ignored):
        self.data = payload
        return True

class SOAPSIOResponse(_Response):
    """ Stores responses from SOAP SIO services.
    """
    def init(self):
        response = objectify.fromstring(self.inner.text)

        soap_fault = soap_fault_xpath(response)
        if soap_fault:
            self.details = soap_fault[0]
        else:
            zato_data = zato_data_xpath(response)
            if not zato_data:
                msg = 'Server did not send a business payload ({} element is missing), soap_response:[{}]'.format(
                    zato_data_path, self.inner.text)
                self.details = msg

            # We have a payload but hadn't there been any errors at the server's side?
            zato_result = zato_result_xpath(response)

            if zato_result[0] == ZATO_OK:
                self.ok = True
                self.data = zato_data[0]
                self.has_data = True
            else:
                self.details = zato_details_xpath(response)[0]

class ServiceInvokeResponse(JSONSIOResponse):
    """ Stores responses from SIO services invoked through the zato.service.invoke service.
    """
    def __init__(self, *args, **kwargs):
        self.inner_service_response = None
        super(ServiceInvokeResponse, self).__init__(*args, **kwargs)

    def set_data(self, payload, has_zato_env):
        response = payload.get('response')
        if response:
            if has_zato_env:
                self.inner_service_response = payload['response'].decode('base64')
                try:
                    data = loads(self.inner_service_response)
                except ValueError:
                    # Not a JSON response
                    self.data = self.inner_service_response
                else:
                    if isinstance(data, dict):
                        self.meta = data.get('_meta')
                        data_keys = data.keys()
                        if len(data_keys) == 1:
                            data_key = data_keys[0]
                            if isinstance(data_key, basestring) and data_key.startswith('zato'):
                                self.data = data[data_key]
                            else:
                                self.data = data
                        else:
                            self.data = data
                    else:
                        self.data = data
            else:
                try:
                    data = loads(response)
                except ValueError:
                    # Not a JSON response
                    self.data = response
                else:
                    self.data = data

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

class _Client(object):
    """ A base class of convenience clients for invoking Zato services from other Python applications.
    """
    def __init__(self, address, path, auth=None, session=None, to_bunch=False,
                 max_response_repr=DEFAULT_MAX_RESPONSE_REPR, max_cid_repr=DEFAULT_MAX_CID_REPR, logger=None,
                 tls_verify=True):
        self.address = address
        self.service_address = '{}{}'.format(address, path)
        self.session = session or requests.session()
        self.to_bunch = to_bunch
        self.max_response_repr = max_response_repr
        self.max_cid_repr = max_cid_repr
        self.logger = logger or mod_logger
        self.tls_verify = tls_verify

        if not self.session.auth:
            self.session.auth = auth

    def inner_invoke(self, request, response_class, async, headers, output_repeated=False):
        """ Actually invokes a service through HTTP and returns its response.
        """
        raw_response = self.session.post(self.service_address, request, headers=headers, verify=self.tls_verify)
        response = response_class(
            raw_response, self.to_bunch, self.max_response_repr,
            self.max_cid_repr, self.logger, output_repeated)

        if self.logger.isEnabledFor(logging.DEBUG):
            msg = 'request:[%s]\nresponse_class:[%s]\nasync:[%s]\nheaders:[%s]\n text:[%s]\ndata:[%s]'
            self.logger.debug(msg, request.decode('utf-8'), response_class, async, headers, raw_response.text, response.data)

        return response

    def invoke(self, request, response_class, async=False, headers=None, output_repeated=False):
        """ Input parameters are like when invoking a service directly.
        """
        headers = headers or {}
        return self.inner_invoke(request, response_class, async, headers)

# ################################################################################################################################

class _JSONClient(_Client):
    """ Base class for all JSON clients.
    """
    response_class = None

    def invoke(self, payload='', headers=None, to_json=True):
        if to_json:
            payload = dumps(payload)
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

class SOAPSIOClient(_Client):
    """ Client for services that accept Simple IO (SIO) in SOAP.
    """
    def invoke(self, soap_action, payload=None, headers=None):
        headers = headers or {}
        headers['SOAPAction'] = soap_action
        return super(SOAPSIOClient, self).invoke(payload, SOAPSIOResponse, headers=headers)

class AnyServiceInvoker(_Client):
    """ Uses zato.service.invoke to invoke other services. The services being invoked
    don't have to be available through any channels, it suffices for zato.service.invoke
    to be exposed over HTTP.
    """
    def json_default_handler(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        raise TypeError('Cannot serialize [{}]'.format(value))

    def _invoke(self, name=None, payload='', headers=None, channel='invoke', data_format='json',
                transport=None, async=False, expiration=BROKER.DEFAULT_EXPIRATION, id=None,
                to_json=True, output_repeated=ZATO_NOT_GIVEN, pid=None, all_pids=False, timeout=None):

        if not(name or id):
            raise ZatoException(msg='Either name or id must be provided')

        if name and output_repeated == ZATO_NOT_GIVEN:
            output_repeated = name.lower().endswith('list')

        if to_json:
            payload = dumps(payload, default=self.json_default_handler)

        id_, value = ('name', name) if name else ('id', id)

        request = {
            id_: value,
            'payload': payload.encode('base64'),
            'channel': channel,
            'data_format': data_format,
            'transport': transport,
            'async': async,
            'expiration':expiration,
            'pid':pid,
            'all_pids': all_pids,
            'timeout': timeout,
        }

        return super(AnyServiceInvoker, self).invoke(dumps(request), ServiceInvokeResponse, async, headers, output_repeated)

    def invoke(self, *args, **kwargs):
        return self._invoke(async=False, *args, **kwargs)

    def invoke_async(self, *args, **kwargs):
        return self._invoke(async=True, *args, **kwargs)

# ################################################################################################################################

class XMLClient(_Client):
    def invoke(self, payload='', headers=None):
        return super(XMLClient, self).invoke(payload, XMLResponse, headers=headers)

class SOAPClient(_Client):
    def invoke(self, soap_action, payload='', headers=None):
        headers = headers or {}
        headers['SOAPAction'] = soap_action
        return super(SOAPClient, self).invoke(payload, SOAPResponse, headers=headers)

# ################################################################################################################################

class RawDataClient(_Client):
    """ Client which doesn't process requests before passing them into a service.
    Likewise, no parsing of response is performed.
    """
    def invoke(self, payload='', headers=None):
        return super(RawDataClient, self).invoke(payload, RawDataResponse, headers=headers)

# ################################################################################################################################

def get_client_from_server_conf(server_dir, client_auth_func, get_config_func, server_url=None):
    """ Returns a Zato client built out of data found in a given server's config files.
    """

    # To avoid circular references
    from zato.common.crypto import ServerCryptoManager
    from zato.common.util import get_odb_session_from_server_config

    class ZatoClient(AnyServiceInvoker):
        def __init__(self, *args, **kwargs):
            super(ZatoClient, self).__init__(*args, **kwargs)
            self.cluster_id = None
            self.odb_session = None

    repo_dir = os.path.join(os.path.abspath(os.path.join(server_dir)), 'config', 'repo')
    cm = ServerCryptoManager.from_repo_dir(None, repo_dir, None)

    secrets_conf = get_config_func(repo_dir, 'secrets.conf', needs_user_config=False)
    config = get_config_func(repo_dir, 'server.conf', crypto_manager=cm, secrets_conf=secrets_conf)
    server_url = server_url if server_url else config.main.gunicorn_bind
    client_auth = client_auth_func(config, repo_dir, cm, False)
    client = ZatoClient('http://{}'.format(server_url), '/zato/admin/invoke', client_auth, max_response_repr=15000)
    session = get_odb_session_from_server_config(config, None, False)

    client.cluster_id = session.query(Server).\
        filter(Server.token == config.main.token).\
        one().cluster_id

    client.odb_session = session

    return client

# ################################################################################################################################
# ################################################################################################################################
