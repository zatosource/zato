# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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
from threading import RLock

# Bunch
from bunch import Bunch

class ConfigDict(object):
    """ Stores configuration of a particular item of interest, such as an
    outgoing HTTP connection. Could've been a dict and we wouldn't have been using
    .get and .set but things like connection names aren't necessarily proper
    Python attribute names. Also, despite certain dict operations being atomic
    in CPython, the class employs a threading.Lock in critical places so the code
    doesn't assume anything about CPython's byte code-specific implementation
    details.
    """
    def __init__(self, name, _dict={}):
        self.name = name
        self._dict = _dict
        self.lock = RLock()
        
    def get(self, key):
        with self.lock:
            return self._dict[key]
        
    def set(self, key, value):
        with self.lock:
            self._dict[key] = value
            
    def __del__(self, key):
        with self.lock:
            del self._dict[key]
            
#    def from_query(self, query, attrs, item_class=

class ConfigStore(object):
    def __init__(self):
        self.ftp = ConfigDict('ftp')
    
def my_test():
    b = Bunch()
    d = dict()
    b.a = 1
    d['a'] = 1
    for x in range(500000):
        #b.a
        d['a']
    
if __name__ == '__main__':
    import cProfile
    cProfile.run('my_test()')
    
# ftp = self.outgoing.ftp.get('aaa')
# plain_http = self.outgoing.plain_http.get('aaa')
# s3 = self.outgoing.s3.get('aaa')
# soap = self.outgoing.soap.get('aaa')
# sql_conn = self.sql_pool.get('aaa')

# del self.outgoing.ftp['aaa']

# config_copy = copy.copy(outgoing)
# ftp_copy = copy.copy(outgoing.ftp)
