# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from copy import deepcopy
from cStringIO import StringIO
from datetime import datetime, timedelta
from json import dumps, loads
from traceback import format_exc

# gevent
import gevent
from gevent.lock import RLock
from gevent.queue import Empty, Queue

# parse
from parse import PARSE_RE

# Requests
import requests

# Zato
from zato.common import DATA_FORMAT, Inactive, SECURITY_TYPES, URL_TYPE, ZatoException
from zato.common.util import get_component_name, new_cid, security_def_type

logger = logging.getLogger(__name__)

# ################################################################################################################################

class BaseHTTPSOAPWrapper(object):
    """ Base class for HTTP/SOAP connections wrappers.
    """
    def __init__(self, config, requests_module=None):
        self.config = config
        self.config_no_sensitive = deepcopy(self.config)
        self.config_no_sensitive['password'] = '***'
        self.requests_module = requests_module or requests
        self.session = self.requests_module.session(pool_maxsize=self.config['pool_size'])
        self._component_name = get_component_name()

        self.address = None
        self.path_params = []

        self.set_address_data()
        self.set_auth()

    def ping(self, cid):
        """ Pings a given HTTP/SOAP resource
        """
        if logger.isEnabledFor(logging.DEBUG):
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
        response = self.session.request(self.config['ping_method'], self.address, 
                auth=self.requests_auth, headers=self._create_headers(cid, {}),
                hooks={'zato_pre_request':zato_pre_request_hook})
        
        # .. store additional info, get and close the stream.
        verbose.write('Code: {}'.format(response.status_code))
        verbose.write('\nResponse time: {}'.format(datetime.utcnow() - start))
        value = verbose.getvalue()
        verbose.close()

        return value

    def _create_headers(self, cid, user_headers):
        headers = {
            'X-Zato-CID': cid,
            'X-Zato-Component':self._component_name,
            'X-Zato-Msg-TS':datetime.utcnow().isoformat(),
            }

        if self.config.get('transport') == URL_TYPE.SOAP:
            headers['SOAPAction'] = self.config.get('soap_action')

        headers.update(user_headers)

        return headers

    def set_auth(self):
        """ Configures the security for requests, if any is to be configured at all.
        """
        self.requests_auth = self.auth if self.config['sec_type'] == security_def_type.basic_auth else None
        if self.config['sec_type'] == security_def_type.wss:
            self.soap[self.config['soap_version']]['header'] = self.soap[self.config['soap_version']]['header_template'].format(
                Username=self.config['username'], Password=self.config['password'])


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
<s11:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s11="http://schemas.xmlsoap.org/soap/envelope/">
  {header}
  <s11:Body>{data}</s11:Body>
</s11:Envelope>"""
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
<s12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s12="http://www.w3.org/2003/05/soap-envelope/">
  {header}
  <s12:Body></s12:Body>
</s12:Envelope>"""
        self.soap['1.2']['header_template'] = """<s12:Header xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" >
          <wsse:Security>
            <wsse:UsernameToken>
              <wsse:Username>{Username}</wsse:Username>
              <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{Password}</wsse:Password>
            </wsse:UsernameToken>
          </wsse:Security>
        </s12:Header>
        """

# ##############################################################################
        
    def __str__(self):
        return '<{} at {}, config:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)
    
    __repr__ = __str__
    
# ##############################################################################

    def format_address(self, cid, params):
        """ Formats a URL path to an external resource. Note that exception raised
        do not contain anything except for CID. This is in order to keep any potentially
        sensitive data from leaking to clients.
        """

        if not params:
            logger.warn('CID:[%s] No parameters given for URL path:[%s]', cid, self.config['address_url_path'])
            raise ValueError('CID:[{}] No parameters given for URL path'.format(cid))
        
        path_params = {}
        try:
            for name in self.path_params:
                path_params[name] = params.pop(name)
            
            return (self.address.format(**path_params), dict(params))
        except KeyError, e:
            logger.warn('CID:[%s] Could not build URL path:[%s] with params:[%s], e:[%s]', 
                cid, self.config['address_url_path'], params, format_exc(e))
            
            raise ValueError('CID:[{}] Could not build URL path'.format(cid))
            
# ##############################################################################

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
        if self.config['sec_type'] in(security_def_type.basic_auth, security_def_type.wss):
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
            
        if self.config['sec_type'] == security_def_type.wss:
            soap_header = soap_config['header']
        else:
            soap_header = ''
            
        return soap_config['message'].format(header=soap_header, data=data), headers
    
# ##############################################################################

    def http_request(self, method, cid, data='', params=None, *args, **kwargs):
        self._enforce_is_active()

        # We never touch strings/unicode because apparently the user already serialized outgoing data
        needs_serialize = not isinstance(data, basestring)

        if needs_serialize:
            if self.config['data_format'] == DATA_FORMAT.JSON:
                data = dumps(data)

        headers = self._create_headers(cid, kwargs.pop('headers', {}))
        if self.config['transport'] == 'soap':
            data, headers = self._soap_data(data, headers)

        params = params or {}

        if self.path_params:
            address, qs_params = self.format_address(cid, params)
        else:
            address, qs_params = self.address, dict(params)

        logger.info('CID:[%s], address:[%s], qs_params:[%s]', cid, address, qs_params)

        response = self.session.request(method, address, data=data,
            auth=self.requests_auth, params=qs_params, headers=headers, *args, **kwargs)

        logger.debug('CID:[%s], response:[%s]', cid, response.text)

        if needs_serialize:
            if self.config['data_format'] == DATA_FORMAT.JSON:
                response.data = loads(response.text)

        return response

# ##############################################################################
    
    def get(self, cid, params=None, *args, **kwargs):
        return self.http_request('GET', cid, '', params, *args, **kwargs)
    
    def delete(self, cid, params=None, *args, **kwargs):
        return self.http_request('DELETE', cid, '', params, *args, **kwargs)
    
    def options(self, cid, params=None, *args, **kwargs):
        return self.http_request('OPTIONS', cid, '', params, *args, **kwargs)
    
# ##############################################################################

    
    def post(self, cid, data='', params=None, *args, **kwargs):
        return self.http_request('POST', cid, data, params, *args, **kwargs)
    
    send = post
    
    def put(self, cid, data='', params=None, *args, **kwargs):
        return self.http_request('PUT', cid, data, params, *args, **kwargs)
    
    def patch(self, cid, data='', params=None, *args, **kwargs):
        return self.http_request('PATCH', cid, data, params, *args, **kwargs)

# ################################################################################################################################

class _SudsClient(object):
    def __init__(self, client_queue, conn_name):
        self.queue = client_queue
        self.conn_name = conn_name
        self.client = None

    def __enter__(self):
        try:
            self.client = self.queue.get(block=False)
        except Empty:
            self.client = None
            msg = 'No free connections to `{}`'.format(self.conn_name)
            logger.error(msg)
            raise Exception(msg)
        else:
            return self.client

    def __exit__(self, type, value, traceback):
        if self.client:
            self.queue.put(self.client)

class _SudsClientQueue(object):
    def __init__(self, queue, conn_name):
        self.queue = queue
        self.conn_name = conn_name

    def __call__(self):
        return _SudsClient(self.queue, self.conn_name)

class SudsSOAPWrapper(BaseHTTPSOAPWrapper):
    """ A thin wrapper around the suds SOAP library
    """
    def __init__(self, config):
        super(SudsSOAPWrapper, self).__init__(config)
        self.update_lock = RLock()
        self.config = config
        self.config_no_sensitive = deepcopy(self.config)
        self.config_no_sensitive['password'] = '***'
        self.client = _SudsClientQueue(Queue(self.config['pool_size']), self.config['name'])

    def build_client_queue(self):

        with self.update_lock:

            # Lazily-imported here to make sure gevent monkey patches everything well in advance
            from suds.client import Client
            from suds.transport.http import HttpAuthenticated
            from suds.transport.https import WindowsHttpAuthenticated
            from suds.wsse import UsernameToken

            url = '{}{}'.format(self.config['address_host'], self.config['address_url_path'])

            def add_client():

                sec_type = self.config['sec_type']
                credentials = {'username':self.config['username'], 'password':self.config['password']}

                if sec_type == security_def_type.ntlm:
                    transport = WindowsHttpAuthenticated(**credentials)

                elif sec_type == security_def_type.basic_auth:
                    transport = HttpAuthenticated(**credentials)

                else:
                    transport = None

                client = Client(url, autoblend=True, transport=transport)

                self.client.queue.put(client)
                logger.debug('Adding Suds SOAP client to [%s]', url)

            for x in range(self.client.queue.maxsize):
                gevent.spawn(add_client)

            start = datetime.utcnow()
            build_until = start + timedelta(seconds=self.config['queue_build_cap'])
    
            while not self.client.queue.full():
                gevent.sleep(0.5)

                now = datetime.utcnow()
                if  now >= build_until:

                    msg = 'Built {}/{} Suds SOAP clients to {} within {} seconds, giving up'.format(
                        self.client.queue.qsize(), self.client.queue.maxsize, url, self.config['queue_build_cap'])
                    logger.error(msg)
                    return

                logger.info('%d/%d Suds SOAP clients connected to `%s` after %s (cap: %ss)',
                    self.client.queue.qsize(), self.client.queue.maxsize, url, now - start, self.config['queue_build_cap'])

            logger.info('Obtained %d Suds SOAP clients to `%s` for `%s`', self.client.queue.maxsize, url, self.config['name'])
