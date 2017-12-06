# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from cStringIO import StringIO
from datetime import datetime
from json import dumps, loads
from logging import DEBUG, getLogger
from traceback import format_exc

# gevent
from gevent.lock import RLock

# lxml
from lxml.etree import fromstring, tostring

# parse
from parse import PARSE_RE

# Requests
import requests
from requests.exceptions import Timeout as RequestsTimeout

# Zato
from zato.common import CONTENT_TYPE, DATA_FORMAT, Inactive, SEC_DEF_TYPE, soapenv11_namespace, soapenv12_namespace, TimeoutException, \
     URL_TYPE, ZATO_NONE
from zato.common.util import get_component_name
from zato.server.connection.queue import ConnectionQueue

logger = getLogger(__name__)

# ################################################################################################################################

class HTTPSAdapter(requests.adapters.HTTPAdapter):
    """ An adapter which exposes a method for clearing out the underlying pool. Useful with HTTPS as it allows to update TLS
    material on fly.
    """
    def clear_pool(self):
        self.poolmanager.clear()

# ################################################################################################################################

class BaseHTTPSOAPWrapper(object):
    """ Base class for HTTP/SOAP connections wrappers.
    """
    def __init__(self, config, requests_module=None):
        self.config = config
        self.config['timeout'] = float(self.config['timeout']) if self.config['timeout'] else 0
        self.config_no_sensitive = deepcopy(self.config)
        self.config_no_sensitive['password'] = '***'
        self.requests_module = requests_module or requests
        self.session = self.requests_module.session(pool_maxsize=self.config['pool_size'])
        self.https_adapter = HTTPSAdapter()
        self.session.mount('https://', self.https_adapter)
        self._component_name = get_component_name()
        self.default_content_type = self.get_default_content_type()

        self.address = None
        self.path_params = []

        self.set_address_data()

    def invoke_http(self, cid, method, address, data, headers, hooks, *args, **kwargs):

        cert = self.config['tls_key_cert_full_path'] if self.config['sec_type'] == SEC_DEF_TYPE.TLS_KEY_CERT else None
        verify = False if self.config.get('tls_verify', ZATO_NONE) == ZATO_NONE else self.config['tls_verify']
        verify = verify if isinstance(verify, bool) else verify.encode('utf-8')

        try:

            # Suds connections don't have requests_auth
            auth = getattr(self, 'requests_auth', None)

            return self.session.request(
                method, address, data=data, auth=auth, headers=headers, hooks=hooks,
                cert=cert, verify=verify, timeout=self.config['timeout'], *args, **kwargs)
        except RequestsTimeout, e:
            raise TimeoutException(cid, format_exc(e))

    def ping(self, cid):
        """ Pings a given HTTP/SOAP resource
        """
        if logger.isEnabledFor(DEBUG):
            msg = 'About to ping:[{}]'.format(self.config_no_sensitive)
            logger.debug(msg)

        # session will write some info to it ..
        verbose = StringIO()

        start = datetime.utcnow()

        def zato_pre_request_hook(hook_data, *args, **kwargs):
            entry = '{} (UTC) {} {}\n'.format(datetime.utcnow().isoformat(),
                hook_data['request'].method, hook_data['request'].url)
            verbose.write(entry)

        # .. invoke the other end ..
        response = self.invoke_http(cid, self.config['ping_method'], self.address, '', self._create_headers(cid, {}),
            {'zato_pre_request':zato_pre_request_hook})

        # .. store additional info, get and close the stream.
        verbose.write('Code: {}'.format(response.status_code))
        verbose.write('\nResponse time: {}'.format(datetime.utcnow() - start))
        value = verbose.getvalue()
        verbose.close()

        return value

    def get_default_content_type(self):

        if self.config['content_type']:
            return self.config['content_type']

        # Set content type only if we know the data format
        if self.config['data_format']:

            # Not SOAP
            if self.config['transport'] == URL_TYPE.PLAIN_HTTP:

                # JSON
                if self.config['data_format'] == DATA_FORMAT.JSON:
                    return CONTENT_TYPE.JSON

                # Plain XML
                elif self.config['data_format'] == DATA_FORMAT.XML:
                    return CONTENT_TYPE.PLAIN_XML

            # SOAP
            elif self.config['transport'] == URL_TYPE.SOAP:

                # SOAP 1.1
                if self.config['soap_version'] == '1.1':
                    return CONTENT_TYPE.SOAP11

                # SOAP 1.2
                elif self.config['soap_version'] == '1.2':
                    return CONTENT_TYPE.SOAP12

    def _create_headers(self, cid, user_headers, now=None):
        headers = {
            'X-Zato-CID': cid,
            'X-Zato-Component': self._component_name,
            'X-Zato-Msg-TS': now or datetime.utcnow().isoformat(),
            }

        if self.config.get('transport') == URL_TYPE.SOAP:
            headers['SOAPAction'] = self.config.get('soap_action')

        content_type = user_headers.pop('Content-Type', self.default_content_type)
        if content_type:
            headers['Content-Type'] = content_type

        headers.update(user_headers)

        return headers

    def set_address_data(self):
        """Sets the full address to invoke and parses input URL's configuration,
        to extract any named parameters that will have to be passed in by users
        during actual calls to the resource.
        """
        self.address = '{}{}'.format(self.config['address_host'], self.config['address_url_path'])
        groups = PARSE_RE.split(self.config['address_url_path'])

        logger.debug('self.address:[%s], groups:[%s]', self.address, groups)

        for group in groups:
            if group and group[0] == '{':
                self.path_params.append(group[1:-1])

        logger.debug('self.address:[%s], self.path_params:[%s]', self.address, self.path_params)

# ################################################################################################################################

class HTTPSOAPWrapper(BaseHTTPSOAPWrapper):
    """ A thin wrapper around the API exposed by the 'requests' package.
    """
    def __init__(self, config, requests_module=None):
        super(HTTPSOAPWrapper, self).__init__(config, requests_module)

        self.soap = {}
        self.soap['1.1'] = {}
        self.soap['1.1']['content_type'] = 'text/xml; charset=utf-8'
        self.soap['1.1']['message'] = """<?xml version="1.0" encoding="utf-8"?>
<s11:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s11="%s">
  {header}
  <s11:Body>{data}</s11:Body>
</s11:Envelope>""" % (soapenv11_namespace,)

        self.soap['1.1']['header_template'] = """<s11:Header xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" >
          <wsse:Security>
            <wsse:UsernameToken>
              <wsse:Username>{Username}</wsse:Username>
              <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{Password}</wsse:Password>
            </wsse:UsernameToken>
          </wsse:Security>
        </s11:Header>
        """

        self.soap['1.2'] = {}
        self.soap['1.2']['content_type'] = 'application/soap+xml; charset=utf-8'
        self.soap['1.2']['message'] = """<?xml version="1.0" encoding="utf-8"?>
<s12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s12="%s">{header}
  <s12:Body>{data}</s12:Body>
</s12:Envelope>""" % (soapenv12_namespace,)

        self.soap['1.2']['header_template'] = """<s12:Header xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" >
          <wsse:Security>
            <wsse:UsernameToken>
              <wsse:Username>{Username}</wsse:Username>
              <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{Password}</wsse:Password>
            </wsse:UsernameToken>
          </wsse:Security>
        </s12:Header>
        """
        self.set_auth()

    def set_auth(self):
        self.requests_auth = self.auth if self.config['sec_type'] == SEC_DEF_TYPE.BASIC_AUTH else None

        if self.config['sec_type'] == SEC_DEF_TYPE.WSS:
            self.soap[self.config['soap_version']]['header'] = \
                self.soap[self.config['soap_version']]['header_template'].format(
                    Username=self.config['username'], Password=self.config['password'])

# ################################################################################################################################

    def __str__(self):
        return '<{} at {}, config:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

    __repr__ = __str__

# ################################################################################################################################

    def format_address(self, cid, params):
        """ Formats a URL path to an external resource. Note that exception raised
        do not contain anything except for CID. This is in order to keep any potentially
        sensitive data from leaking to clients.
        """

        if not params:
            logger.warn('CID:[%s] No parameters given for URL path:`%r`', cid, self.config['address_url_path'])
            raise ValueError('CID:[{}] No parameters given for URL path'.format(cid))

        path_params = {}
        try:
            for name in self.path_params:
                path_params[name] = params.pop(name)

            return (self.address.format(**path_params), dict(params))
        except(KeyError, ValueError), e:
            logger.warn('CID:[%s] Could not build URL address `%r` path:`%r` with params:`%r`, e:`%s`',
                cid, self.address, self.config['address_url_path'], params, format_exc(e))

            raise ValueError('CID:[{}] Could not build URL path'.format(cid))

# ################################################################################################################################

    def _impl(self):
        """ Returns the self.session object through which access to HTTP/SOAP
        resources is mediated.
        """
        return self.session

    impl = property(fget=_impl, doc=_impl.__doc__)

    def _get_auth(self):
        """ Returns a username and password pair or None, if no security definition
        has been attached.
        """
        if self.config['sec_type'] in (SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.WSS):
            auth = (self.config['username'], self.config['password'])
        else:
            auth = None

        return auth

    auth = property(fget=_get_auth, doc=_get_auth)

    def _enforce_is_active(self):
        if not self.config['is_active']:
            raise Inactive(self.config['name'])

    def _soap_data(self, data, headers):
        """ Wraps the data in a SOAP-specific messages and adds the headers required.
        """
        soap_config = self.soap[self.config['soap_version']]

        # The idea here is that even though there usually won't be the Content-Type
        # header provided by the user, we shouldn't overwrite it if one has been
        # actually passed in.
        if not headers.get('Content-Type'):
            headers['Content-Type'] = soap_config['content_type']

        if self.config['sec_type'] == SEC_DEF_TYPE.WSS:
            soap_header = soap_config['header']
        else:
            soap_header = ''

        return soap_config['message'].format(header=soap_header, data=data), headers

# ################################################################################################################################

    def http_request(self, method, cid, data='', params=None, *args, **kwargs):
        self._enforce_is_active()

        # We never touch strings/unicode because apparently the user already serialized outgoing data
        needs_serialize = not isinstance(data, basestring)

        if needs_serialize:
            if self.config['data_format'] == DATA_FORMAT.JSON:
                data = dumps(data)
            elif data and self.config['data_format'] == DATA_FORMAT.XML:
                data = tostring(data)

        headers = self._create_headers(cid, kwargs.pop('headers', {}))
        if self.config['transport'] == 'soap':
            data, headers = self._soap_data(data, headers)

        params = params or {}

        if self.path_params:
            address, qs_params = self.format_address(cid, params)
        else:
            address, qs_params = self.address, dict(params)

        if isinstance(data, unicode):
            data = data.encode('utf-8')

        logger.info(
            'CID:`%s`, address:`%s`, qs:`%s`, auth:`%s`, kwargs:`%s`', cid, address, qs_params, self.requests_auth, kwargs)

        response = self.invoke_http(cid, method, address, data, headers, {}, params=qs_params, *args, **kwargs)

        if logger.isEnabledFor(DEBUG):
            logger.debug('CID:`%s`, response:`%s`', cid, response.text)

        if needs_serialize:

            if self.config['data_format'] == DATA_FORMAT.JSON:
                response.data = loads(response.text)

            elif self.config['data_format'] == DATA_FORMAT.XML:
                if response.text and response.headers.get('Content-Type') in ('application/xml', 'text/xml'):
                    response.data = fromstring(response.text)

        return response

# ################################################################################################################################

    def get(self, cid, params=None, *args, **kwargs):
        return self.http_request('GET', cid, '', params, *args, **kwargs)

    def delete(self, cid, params=None, *args, **kwargs):
        return self.http_request('DELETE', cid, '', params, *args, **kwargs)

    def options(self, cid, params=None, *args, **kwargs):
        return self.http_request('OPTIONS', cid, '', params, *args, **kwargs)

# ################################################################################################################################

    def post(self, cid, data='', params=None, *args, **kwargs):
        return self.http_request('POST', cid, data, params, *args, **kwargs)

    send = post

    def put(self, cid, data='', params=None, *args, **kwargs):
        return self.http_request('PUT', cid, data, params, *args, **kwargs)

    def patch(self, cid, data='', params=None, *args, **kwargs):
        return self.http_request('PATCH', cid, data, params, *args, **kwargs)

# ################################################################################################################################

class SudsSOAPWrapper(BaseHTTPSOAPWrapper):
    """ A thin wrapper around the suds SOAP library
    """
    def __init__(self, config):
        super(SudsSOAPWrapper, self).__init__(config)
        self.set_auth()
        self.update_lock = RLock()
        self.config = config
        self.config['timeout'] = float(self.config['timeout'])
        self.config_no_sensitive = deepcopy(self.config)
        self.config_no_sensitive['password'] = '***'
        self.address = '{}{}'.format(self.config['address_host'], self.config['address_url_path'])
        self.conn_type = 'Suds SOAP'
        self.client = ConnectionQueue(
            self.config['pool_size'], self.config['queue_build_cap'], self.config['name'], self.conn_type, self.address,
            self.add_client)

    def set_auth(self):
        """ Configures the security for requests, if any is to be configured at all.
        """
        self.suds_auth = {'username':self.config['username'], 'password':self.config['password']}

    def add_client(self):

        logger.info('About to add a client to `%s` (%s)', self.address, self.conn_type)

        try:

            # Lazily-imported here to make sure gevent monkey patches everything well in advance
            from suds.client import Client
            from suds.transport.https import HttpAuthenticated
            from suds.transport.https import WindowsHttpAuthenticated
            from suds.wsse import Security, UsernameToken

            sec_type = self.config['sec_type']

            if sec_type == SEC_DEF_TYPE.BASIC_AUTH:
                transport = HttpAuthenticated(**self.suds_auth)

            elif sec_type == SEC_DEF_TYPE.NTLM:
                transport = WindowsHttpAuthenticated(**self.suds_auth)

            elif sec_type == SEC_DEF_TYPE.WSS:
                security = Security()
                token = UsernameToken(self.suds_auth['username'], self.suds_auth['password'])
                security.tokens.append(token)

                client = Client(self.address, autoblend=True, wsse=security)

            if sec_type in(SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.NTLM):
                client = Client(self.address, autoblend=True, transport=transport)

            # Still could be either none at all or WSS
            if not sec_type:
                client = Client(self.address, autoblend=True, timeout=self.config['timeout'])

            self.client.put_client(client)

        except Exception, e:
            logger.warn('Error while adding a SOAP client to `%s` (%s) e:`%s`', self.address, self.conn_type, format_exc(e))

    def build_client_queue(self):

        with self.update_lock:
            self.client.build_queue()

# ################################################################################################################################
