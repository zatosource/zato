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
from copy import deepcopy
from threading import RLock

# mx
from mx.Tools import NotGiven

# Paste
from paste.util.multidict import MultiDict

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
    def __init__(self, name, _bunch=None):
        self.name = name
        self._bunch = _bunch
        self.lock = RLock()
        
    def get(self, key, default=None):
        with self.lock:
            return self._bunch.get(key, default)
        
    __getitem__ = get
        
    def set(self, key, value):
        with self.lock:
            self._bunch[key] = value
            
    __setitem__ = set
            
    def __delitem__(self, key):
        with self.lock:
            del self._bunch[key]
            
    def __iter__(self):
        with self.lock:
            return iter(self._bunch)
        
    def __repr__(self):
        with self.lock:
            return '<{} at {} keys:[{}]>'.format(self.__class__.__name__,
                hex(id(self)), sorted(self._bunch.keys()))
        
    __str__ = __repr__
    
    def __nonzero__(self):
        with self.lock:
            return bool(self._bunch)
            
    def copy(self):
        """ Returns a new instance of ConfigDict with items copied over from self.
        """
        config_dict = ConfigDict(self.name)
        config_dict._bunch = Bunch()
        config_dict._bunch.update(self._bunch)
        
        return config_dict
    
    def copy_keys(self):
        """ Returns a deepcopy of the underlying Bunch's keys
        """
        with self.lock:
            return deepcopy(self._bunch.keys())
            
    @staticmethod        
    def from_query(name, query_data, item_class=Bunch):
        """ Return a new ConfigDict with items taken from an SQL query.
        """
        config_dict = ConfigDict(name)
        config_dict._bunch = Bunch()
        
        if query_data:
            query, attrs = query_data
    
            for item in query:
                config_dict._bunch[item.name] = Bunch()
                config_dict._bunch[item.name].config = Bunch()
                
                for attr_name in attrs.keys():
                    config_dict._bunch[item.name]['config'][attr_name] = getattr(item, attr_name)
            
        return config_dict

class ConfigStore(object):
    """ The central place for storing a Zato server's thread configuration. 
    May /not/ be shared across threads - each thread should get its own copy
    using the .copy method.
    
    Note that much more should be stored in here but the work is not finished yet -
    for instance, connection definitions should be kept here.
    """
    def __init__(self, out_ftp=NotGiven, out_plain_http=NotGiven, out_soap=NotGiven, out_s3=NotGiven, 
                 out_sql=NotGiven, repo_location=NotGiven, basic_auth=NotGiven, wss=NotGiven, tech_acc=NotGiven,
                 url_sec=NotGiven, http_soap=NotGiven, broker_config=NotGiven, odb_data=NotGiven,
                 simple_io=NotGiven):
        
        # Outgoing connections
        self.out_ftp = out_ftp
        self.out_plain_http = out_plain_http
        self.out_soap = out_soap
        self.out_s3 = out_s3
        self.out_sql = out_sql
        
        # Local on-disk configuraion repository
        self.repo_location = repo_location
        
        # Security definitions
        self.basic_auth = basic_auth
        self.wss = wss
        self.tech_acc = tech_acc
        
        # URL security
        self.url_sec = url_sec
        
        # HTTP/out_soap channels
        self.http_soap = http_soap
        
        # Configuration for broker clients
        self.broker_config = broker_config

        # ODB
        self.odb_data = odb_data
        
        # SimpleIO
        self.simple_io = simple_io
        
    def outgoing_connections(self):
        """ Returns all the outgoing connections.
        """
        return self.out_ftp, self.out_plain_http, self.out_soap, self.out_s3
        
    def copy(self):
        """ Creates a copy of this ConfigStore. All configuration data is copied
        over except for SQL connections.
        """
        config_store = ConfigStore()
        
        # Grab all ConfigDicts - even if they're actually NotGiven - and make their copies
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, ConfigDict):
                copy_meth = getattr(attr, 'copy')
                setattr(config_store, attr_name, copy_meth())
            elif attr is NotGiven:
                setattr(config_store, attr_name, NotGiven)
                
        http_soap = MultiDict()
        dict_of_lists = self.http_soap.dict_of_lists()
        for url_path, lists in dict_of_lists.items():
            _info = Bunch()
            for elem in lists:
                for soap_action, item in elem.items():
                    _info[soap_action] = Bunch()
                    _info[soap_action].id = item.id
                    _info[soap_action].name = item.name
                    _info[soap_action].is_internal = item.is_internal
                    _info[soap_action].url_path = item.url_path
                    _info[soap_action].method = item.method
                    _info[soap_action].soap_version = item.soap_version
                    _info[soap_action].service_id = item.service_id
                    _info[soap_action].service_name = item.service_name
                    _info[soap_action].impl_name = item.impl_name
                    _info[soap_action].transport = item.transport
                    _info[soap_action].connection = item.connection
            http_soap.add(url_path, _info)
        
        config_store.http_soap = http_soap
        config_store.url_sec = self.url_sec
        config_store.broker_config = self.broker_config
        config_store.odb_data = deepcopy(self.odb_data)
                
        return config_store
    
#
# out_ftp = self.outgoing.out_ftp.get('aaa')
# ------------------------------------
# self.outgoing -> ConfigStore
# self.outgoing.ftp -> ConfigDict
# self.outgoing.ftp.get('aaa') -> Bunch
# self.outgoing.ftp.get('aaa').config -> connection parameters
# self.outgoing.ftp.get('aaa').conn -> connection object
#

# out_amqp = self.outgoing.amqp.get('aaa')
# out_jms_wmq = self.outgoing.jms_wmq.get('aaa')
# out_zmq = self.outgoing.zmq.get('aaa')

# out_ftp = self.outgoing.ftp.get('aaa')
# out_plain_http = self.outgoing.plain_http.get('aaa')
# out_s3 = self.outgoing.s3.get('aaa')
# out_soap = self.outgoing.soap.get('aaa')
# out_sql_conn = self.sql_pool.get('aaa')
# del self.outgoing.ftp['aaa']

# config_copy = copy.copy(outgoing)
# out_ftp_copy = copy.copy(outgoing.ftp)

# with closing(self.server.odb.session()) as session:
# with self.odb.session() as session: