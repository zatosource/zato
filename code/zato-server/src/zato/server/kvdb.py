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
from importlib import import_module

# redis
from redis import StrictRedis

class KVDB(object):
    """ A wrapper around the Zato's key-value database.
    """
    def __init__(self, conn=None, config=None, server=None):
        self.conn = conn
        self.config = config
        self.server = server
        
    def init(self):
        config = {}
        
        if self.config.get('host'):
            config['host'] = self.config.host
        
        if self.config.get('port'):
            config['port'] = int(self.config.port)
            
        if self.config.get('db'):
            config['db'] = int(self.config.db)
            
        if self.config.get('password'):
            config['password'] = self.server.decrypt(self.config.password)
            
        if self.config.get('socket_timeout'):
            config['socket_timeout'] = float(self.config.socket_timeout)
            
        if self.config.get('connection_pool'):
            split = self.config.connection_pool.split('.')
            module, class_name = split[:-1], split[-1]
            mod = import_module(module)
            config['connection_pool'] = getattr(mod, class_name)
            
        if self.config.get('charset'):
            config['charset'] = self.config.charset
            
        if self.config.get('errors'):
            config['errors'] = self.config.errors
            
        if self.config.get('unix_socket_path'):
            config['unix_socket_path'] = self.config.unix_socket_path
            
        self.conn = StrictRedis(**config)
