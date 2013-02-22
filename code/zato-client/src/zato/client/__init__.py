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
    
    def invoke(self, *args, **kwargs):
        """ Input parameters are like when invoking a service directly.
        """
        return self._invoke(*args, async=True, **kwargs)
    
    def invoke_async(self, *args, **kwargs):
        """ Input parameters are like when invoking a service directly.
        """
        return self._invoke(*args, async=True, **kwargs)
        
class InvokeServiceClient(Client):
    def __init__(self, url=None, auth=None, path='/zato/admin/invoke', session=None, to_bunch=True):
        super(InvokeServiceClient, self).__init__(url, auth, path, session, to_bunch)
        
    def _invoke(self, name, payload='', channel='invoke', data_format='json', transport=None, async=False, id=None):
        if name and id:
            msg = 'Cannot use both name:[{}] and id:[{}]'.format(name, id)
            raise ZatoException(msg)
        
        if name:
            id_, value = 'name', name
        else:
            id_, value = 'id', id
        
        request = {
            id_: value,
            'payload': dumps(payload).encode('base64'),
            'channel': channel,
            'data_format': data_format,
            'transport': transport,
            }
        
        response = self.session.post(self.address, dumps(request))
        return Response(response, self.to_bunch)
        
class Response(object):
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
        json = loads(self.inner.text)
        for name in('cid', 'details', 'result'):
            setattr(self, name, json['zato_env'][name])
        self.ok = self.result == ZATO_OK
        
        if self.ok:
            # There will be two keys, zato_env and the actual payload
            for key, value in json.items():
                if key != 'zato_env':
                    if value['response']:
                        data = loads(value['response'].decode('base64'))
                        data_key = data.keys()[0]
                        self.data = bunchify(data[data_key]) if self.to_bunch else data[data_key]
                        self.has_data = True

if __name__ == '__main__':
    client = InvokeServiceClient('http://localhost:17010', ('admin.invoke', 'cdaa6ca6ae944f4bae70d5697162435e'))
    response = client.invoke('zato.service.get-by-name', {'cluster_id':1, 'name':'zato.service.get-by-name'})
    #print(response.inner.text)
    print(response.data)
    
