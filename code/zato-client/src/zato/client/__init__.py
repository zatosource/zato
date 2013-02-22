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
from anyjson import dumps

# requests
import requests

# Zato
from zato.common import ZatoException

logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)

class Client(object):
    """ A convenience client for invoking Zato services from other Python applications.
    """
    def __init__(self, url=None, auth=None, path='/zato/admin/invoke', session=None):
        self.address = '{}{}'.format(url, path)
        self.session = session or self._get_session(auth)
        
    def _get_session(self, auth):
        session = requests.session()
        session.auth = auth
        
        return session
    
    def _invoke(self, name, payload='', channel=None, data_format=None, transport=None, async=False, id=None):
        if name and id:
            msg = 'Cannot use both name:[{}] and id:[{}]'.format(name, id)
            raise ZatoException(msg)
        
        if name:
            id_, value = 'name', name
        else:
            id_, value = 'id', id
        
        request = {
            id_: value,
            'payload': payload.encode('base64'),
            'channel': channel,
            'data_format': data_format,
            'transport': transport,
            }
        
        self.session.post(self.address, dumps(request))
        
        logger.info(request)
        
    def invoke(self, *args, **kwargs):
        """ Works exactly like any service's .invoke method.
        """
        return self._invoke(*args, async=True, **kwargs)
    
    def invoke_async(self, *args, **kwargs):
        """ Works exactly like any service's .invoke_async method.
        """
        return self._invoke(*args, async=True, **kwargs)
    
if __name__ == '__main__':
    client = Client('http://localhost:17010', ('admin.invoke', '4bfad87229044cdd97407984ce00482fx'))
    client.invoke('zato.helpers.input-logger', 'zzz')
