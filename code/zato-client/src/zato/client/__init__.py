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
from logging import getLogger

# anyjson
from anyjson import dumps, loads

# Bunch
from bunch import bunchify

# requests
import requests

# Zato
from zato.common import ZatoException, ZATO_OK

logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)

class Client(object):
    """ A convenience client for invoking Zato services from other Python applications.
    """
    def __init__(self, url=None, auth=None, path=None, session=None, to_bunch=False):
        self.address = '{}{}'.format(url, path)
        self.session = session or requests.session(auth=auth)
        self.to_bunch = to_bunch
        
    def inner_invoke(self, request, response_class, is_async):
        """ Actually invokes a service and returns its response.
        """
        response = self.session.post(self.address, request)
        return response_class(response, self.to_bunch)
    
    def invoke(self, request, response_class):
        """ Input parameters are like when invoking a service directly.
        """
        return self.inner_invoke(request, response_class, False)
    
    def invoke_async(self, request, response_class):
        """ Input parameters are like when invoking a service directly.
        """
        return self.inner_invoke(request, response_class, True)
        
class AnyServiceInvoker(Client):
    """ Uses zato.service.invoke to invoke other services. The services being invoked
    don't have to be available through any channels, it suffices for zato.service.invoke
    to be exposed over HTTP.
    """
    def __init__(self, url=None, auth=None, path='/zato/admin/invoke', session=None, to_bunch=True):
        super(AnyServiceInvoker, self).__init__(url, auth, path, session, to_bunch)
        
    def invoke(self, name, payload='', channel='invoke', data_format='json', transport=None, async=False, id=None):
        id_, value = ('name', name) if name else ('id', id)
        request = { id_: value, 'payload': dumps(payload).encode('base64'),
            'channel': channel, 'data_format': data_format, 'transport': transport,
            }

        return super(AnyServiceInvoker, self).invoke(dumps(request), ServiceInvokeResponse)

class SIOClient(Client):
    """ Client for services that accept Simple IO (SIO).
    """
    def invoke(self, payload=None):
        return super(SIOClient, self).invoke(dumps(payload), SIOResponse)
        
class Response(object):
    """ A base class for all specific response types client may return.
    """
    def __init__(self, inner, to_bunch):
        self.inner = inner # Acutal response from the requests module
        self.to_bunch = to_bunch
        self.result = None
        self.ok = None
        self.has_data = None
        self.data = None
        self.cid = None
        self.details = None
        self.init()
    
    def init(self):
        raise NotImplementedError('Must be defined by subclasses')
        
class SIOResponse(Response):
    """ Stores responses from SIO services.
    """
    def init(self):
        json = loads(self.inner.text)
        for name in('cid', 'details', 'result'):
            setattr(self, name, json['zato_env'][name])
        self.ok = self.result == ZATO_OK
        
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
                        
class ServiceInvokeResponse(SIOResponse):
    """ Stores responses from SIO services invoked through the zato.service.invoke service.
    """
    def set_data(self, payload):
        if payload.get('response'):
            data = loads(payload['response'].decode('base64'))
            data_key = data.keys()[0]
            self.data = data[data_key]
            
            return True 

if __name__ == '__main__':
    address = 'http://localhost:17010'
    auth = ('admin.invoke', 'cdaa6ca6ae944f4bae70d5697162435e')
    path = '/zato/json/zato.security.wss.get-list'
    service = 'zato.helpers.input-logger'
    
    #client = AnyServiceInvoker(address, auth)#, path)
    client = SIOClient(address, auth, path)
    response = client.invoke({'cluster_id':1})
    #print(response.inner.text)
    print(response.data)
    
