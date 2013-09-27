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
from datetime import datetime

# Requests
import requests

# Zato
from zato.common import Inactive, URL_TYPE
from zato.common.util import get_component_name, security_def_type

logger = logging.getLogger(__name__)

class HTTPSOAPWrapper(object):
    """ A thin wrapper around the API exposed by the 'requests' package.
    """
    def __init__(self, config, requests_module=None):
        self.config = config
        self.config_no_sensitive = deepcopy(self.config)
        self.config_no_sensitive['password'] = '***'
        self.requests_module = requests_module or requests
        self.session = self.requests_module.session(pool_maxsize=self.config['pool_size'])
        
        self._component_name = get_component_name()
        
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
        
        self.set_auth()
        
    def set_auth(self):
        """ Configures the security for requests, if any is to be configured at all.
        """
        self.requests_auth = self.auth if self.config['sec_type'] == security_def_type.basic_auth else None
        if self.config['sec_type'] == security_def_type.wss:
            self.soap[self.config['soap_version']]['header'] = self.soap[self.config['soap_version']]['header_template'].format(
                Username=self.config['username'], Password=self.config['password'])
        
    def __str__(self):
        return '<{} at {}, config:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)
    
    __repr__ = __str__
    
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
    
    def _enforce_is_active(self):
        if not self.config['is_active']:
            raise Inactive(self.config['name'])
    
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
        response = self.session.request(self.config['ping_method'], self.config['address'], 
                auth=self.requests_auth, headers=self._create_headers(cid, {}),
                hooks={'zato_pre_request':zato_pre_request_hook})
        
        # .. store additional info, get and close the stream.
        verbose.write('Code: {}'.format(response.status_code))
        verbose.write('\nResponse time: {}'.format(datetime.utcnow() - start))
        value = verbose.getvalue()
        verbose.close()
        
        return value
    
    def get(self, cid, params=None, prefetch=True, *args, **kwargs):
        """ Invokes a resource using the GET method.
        """
        self._enforce_is_active()
        
        headers = self._create_headers(cid, kwargs.pop('headers', {}))
        return self.session.get(self.config['address'], params=params or {}, 
            auth=self.requests_auth, headers=headers, *args, **kwargs)
    
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
    
    def post(self, cid, data='', prefetch=True, *args, **kwargs):
        """ Invokes a resource using the POST method.
        """
        self._enforce_is_active()
        
        headers = self._create_headers(cid, kwargs.pop('headers', {}))
        if self.config['transport'] == 'soap':
            data, headers = self._soap_data(data, headers)

        return self.session.post(self.config['address'], data=data, 
            auth=self.requests_auth, headers=headers, *args, **kwargs)
    
    send = post
