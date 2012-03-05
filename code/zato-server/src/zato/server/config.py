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
from bunch import SimpleBunch

class ConfigDict(object):
    """ Stores configuration of a particular item of interest, such as an
    outgoing HTTP connection. Could've been a dict and we wouldn't have been using
    .get and .set but things like connection names aren't necessarily proper
    Python attribute names. Also, despite certain dict operations being atomic
    in CPython, the class employs a threading.Lock in critical places so the code
    doesn't assume anything about CPython's byte code-specific implementation
    details.
    """
    def __init__(self, name, _bunch={}):
        self.name = name
        self._bunch = _bunch
        self.lock = RLock()
        
    def get(self, key):
        with self.lock:
            return self._bunch[key]
        
    def set(self, key, value):
        with self.lock:
            self._bunch[key] = value
            
    def __del__(self, key):
        with self.lock:
            del self._bunch[key]
            
    @staticmethod        
    def from_query(query_data, item_class=SimpleBunch):
        bunch = SimpleBunch()

        if query_data:
            query, attrs = query_data
    
            for item in query:
                bunch[item.name] = SimpleBunch()
                bunch[item.name].config = SimpleBunch()
                
                for attr_name in attrs.keys():
                    bunch[item.name]['config'][attr_name] = getattr(item, attr_name)
            
        return bunch

class ConfigStore(object):
    def __init__(self, ftp=None, plain_http=None, soap=None, s3=None, 
                 sql_conn=None, amqp=None, jms_wmq=None, zmq=None,
                 repo_location=None, basic_auth=None, wss=None, tech_acc=None,
                 url_sec=None, http_soap=None, broker_config=None):
        
        # Outgoing connections
        self.ftp = ftp                              # done
        self.plain_http = plain_http                # not yet
        self.soap = soap                            # not yet
        self.s3 = s3                                # not yet
        self.sql_conn = sql_conn                    # not yet
        self.amqp = amqp                            # not yet
        self.jms_wmq = jms_wmq                      # not yet
        self.zmq = zmq                              # not yet
        
        # Local on-disk configuraion repository
        self.repo_location = repo_location          # done
        
        # Security definitions
        self.basic_auth = basic_auth                # done
        self.wss = wss                              # not yet
        self.tech_acc = tech_acc                    # not yet
        
        # URL security
        self.url_sec = url_sec                      # done
        
        # HTTP/SOAP channels
        self.http_soap = http_soap                  # done
        
        # Configuration for broker clients
        self.broker_config = broker_config

    
#
# ftp = self.outgoing.ftp.get('aaa')
# ------------------------------------
# self.outgoing -> ConfigStore
# self.outgoing.ftp -> ConfigDict
# self.outgoing.ftp.get('aaa') -> SimpleBunch
# self.outgoing.ftp.get('aaa').config -> connection parameters
# self.outgoing.ftp.get('aaa').conn -> connection object
#

# amqp = self.outgoing.amqp.get('aaa')
# jms_wmq = self.outgoing.jms_wmq.get('aaa')
# zmq = self.outgoing.zmq.get('aaa')

# ftp = self.outgoing.ftp.get('aaa')
# plain_http = self.outgoing.plain_http.get('aaa')
# s3 = self.outgoing.s3.get('aaa')
# soap = self.outgoing.soap.get('aaa')
# sql_conn = self.sql_pool.get('aaa')
# del self.outgoing.ftp['aaa']

# config_copy = copy.copy(outgoing)
# ftp_copy = copy.copy(outgoing.ftp)
