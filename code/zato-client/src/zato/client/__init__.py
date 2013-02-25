# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# anyjson
from anyjson import dumps, loads

# Bunch
from bunch import bunchify

# lxml
from lxml import objectify

# requests
import requests

# Zato
from zato.common import soap_doc, soap_body_path, soap_data_path, soap_data_xpath, soap_fault_xpath, \
     ZatoException, zato_data_path, zato_data_xpath, zato_details_xpath, ZATO_OK, zato_result_xpath
from zato.common.log_message import CID_LENGTH

# Set max_cid_repr to CID_NO_CLIP if it's desired to return the whole of a CID
# in a response's __repr__ method.
CID_NO_CLIP = int(CID_LENGTH / 2)

# ##############################################################################

class _Response(object):
    """ A base class for all specific response types client may return.
    """
    def __init__(self, inner, to_bunch, max_response_repr, max_cid_repr):
        self.inner = inner # Acutal response from the requests module
        self.to_bunch = to_bunch
        self.max_response_repr = max_response_repr
        self.max_cid_repr = max_cid_repr
        self.sio_result = None
        self.ok = False
        self.has_data = False
        self.data = None
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
    
    def init(self):
        raise NotImplementedError('Must be defined by subclasses')
    
# ##############################################################################

class _StructuredResponse(_Response):
    """ Any non-raw and non-SIO response.
    """
    def init(self):
        if self.set_data():
            self.set_has_data()
            self.set_ok()
            
    def _set_data_details(self):
        try:
            self.data = self.load_func(self.inner.text)
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
    
    def set_data(self):
        if self._set_data_details():
            data = self.xpath(self.data)
            if not data:
                self.details = 'No {} in SOAP response'.format(self.path)
            else:
                self.data = data[0]
                return True                
        
# ##############################################################################

class JSONSIOResponse(_Response):
    """ Stores responses from JSON SIO services.
    """
    def init(self):
        json = loads(self.inner.text)
        self.details = json['zato_env']['details']
        self.sio_result = json['zato_env']['result']
        self.ok = self.sio_result == ZATO_OK
        
        if self.ok:
            # There will be two keys, zato_env and the actual payload
            for key, value in json.items():
                if key != 'zato_env':
                    if self.set_data(value):
                        self.has_data = True
                        if self.to_bunch:
                            self.data = bunchify(self.data)
                    
    def set_data(self, payload):  
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
    def set_data(self, payload):
        if payload.get('response'):
            data = loads(payload['response'].decode('base64'))
            data_key = data.keys()[0]
            self.data = data[data_key]
            
            return True 
    
# ##############################################################################
                        
class RawDataResponse(_Response):
    """ Stores responses from services that weren't invoked using any particular
    data format
    """
    def init(self):
        self.ok = self.inner.ok
        if self.set_data():
            self.has_data = True
        
    def set_data(self):
        self.data = self.inner.text
        return len(self.data) > 0
    
# ##############################################################################

class _Client(object):
    """ A base class of convenience clients for invoking Zato services from other Python applications.
    """
    def __init__(self, url=None, auth=None, path=None, session=None, to_bunch=False, 
                     max_response_repr=2500, max_cid_repr=5, logger=None):
        self.address = '{}{}'.format(url, path)
        self.session = session or requests.session(auth=auth)
        self.to_bunch = to_bunch
        self.max_response_repr = max_response_repr
        self.max_cid_repr = max_cid_repr
        self.logger = logger
        
    def inner_invoke(self, request, response_class, is_async, headers):
        """ Actually invokes a service through HTTP and returns its response.
        """
        response = self.session.post(self.address, request, headers=headers)
        return response_class(response, self.to_bunch, self.max_response_repr,
            self.max_cid_repr)
    
    def invoke(self, request, response_class, headers=None):
        """ Input parameters are like when invoking a service directly.
        """
        headers = headers or {}
        return self.inner_invoke(request, response_class, False, headers)
    
# ##############################################################################

class _JSONClient(_Client):
    """ Base class for all JSON clients.
    """
    response_class = None
    
    def invoke(self, payload=None, headers=None):
        return super(_JSONClient, self).invoke(dumps(payload), self.response_class, headers)

class JSONClient(_JSONClient):
    """ Client for services that accept JSON input.
    """
    response_class = JSONResponse
    
# ##############################################################################

class JSONSIOClient(_JSONClient):
    """ Client for services that accept Simple IO (SIO) in JSON.
    """
    response_class = JSONSIOResponse
    
class SOAPSIOClient(_Client):
    """ Client for services that accept Simple IO (SIO) in SOAP.
    """
    def invoke(self, soap_action, payload=None, headers=None):
        headers = headers or {'SOAPAction':soap_action}
        return super(SOAPSIOClient, self).invoke(payload, SOAPSIOResponse, headers)
    
class AnyServiceInvoker(_Client):
    """ Uses zato.service.invoke to invoke other services. The services being invoked
    don't have to be available through any channels, it suffices for zato.service.invoke
    to be exposed over HTTP.
    """
    def invoke(self, name, payload='', headers=None, channel='invoke', data_format='json', transport=None, async=False, id=None):
        id_, value = ('name', name) if name else ('id', id)
        request = { id_: value, 'payload': dumps(payload).encode('base64'),
            'channel': channel, 'data_format': data_format, 'transport': transport,
            }

        return super(AnyServiceInvoker, self).invoke(dumps(request), ServiceInvokeResponse, headers)
    
# ##############################################################################
    
class XMLClient(_Client):
    def invoke(self, payload='', headers=None):
        return super(XMLClient, self).invoke(payload, XMLResponse, headers)
    
class SOAPClient(_Client):
    def invoke(self, soap_action, payload='', headers=None):
        headers = headers or {'SOAPAction':soap_action}
        return super(SOAPClient, self).invoke(payload, SOAPResponse, headers)
    
# ##############################################################################
    
class RawDataClient(_Client):
    """ Client which doesn't process requests before passing them into a service.
    Likewise, no parsing of response is performed.
    """
    def invoke(self, payload='', headers=None):
        return super(RawDataClient, self).invoke(payload, RawDataResponse, headers)
    
# ##############################################################################