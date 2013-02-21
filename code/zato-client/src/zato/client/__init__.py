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

# requests
import requests

logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)

class Client(object):
    """ A convenience client for invoking Zato services from other Python applications.
    """
    def __init__(self, url=None, session=None, auth=None):
        self.url = url
        self.session = session or self._get_session(self.url)
        
    def _get_session(self, url, auth):
        session = requests.session()
        session.auth = auth
    
    def invoke(self, name, payload='', channel=None, data_format=None, transport=None, async=False):
        request = {
            }
        logger.info(name)
    
    def invoke_async(self, *args, **kwargs):
        return self.invoke(*args, async=True, **kwargs)
    
if __name__ == '__main__':
    client = Client('http://localhost:17010')
    client.invoke_async('zzz')
