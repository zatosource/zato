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
from random import choice, randint
from unittest import TestCase
from uuid import uuid4

# anyjson
from anyjson import dumps

# mock
from mock import MagicMock

# Zato
from zato.common.util import new_cid

def rand_int(start=1, stop=100):
    return randint(start, stop)

def rand_string():
    return uuid4().hex

def rand_bool():
    return choice((True, False))

class Expected(object):
    """ A container for the data a test expects the service to return.
    """
    def __init__(self):
        self.data = []
        
    def add(self, item):
        self.data.append(item)
        
    def get_data(self):
        if not self.data or len(self.data) > 1:
            return self.data
        else:
            return self.data[0]

class FakeKVDB(object):
    class FakeConn(object):
        def return_none(self, *ignored_args, **ignored_kwargs):
            return None
        
        get = hget = return_none
        
    def __init__(self):
        self.conn = self.FakeConn()
        
    def translate(self, *ignored_args, **ignored_kwargs):
        raise NotImplementedError()

class FakeServices(object):
    def __getitem__(self, ignored):
        return {'slow_threshold': 1234}
    
class FakeServiceStore(object):
    def __init__(self):
        self.services = FakeServices()
        
class FakeServer(object):
    """ A fake mock server used in test cases.
    """
    def __init__(self):
        self.kvdb = FakeKVDB()
        self.service_store = FakeServiceStore()
        
class ServiceTestCase(TestCase):
    
    def invoke(self, class_, request, expected):
        """ Sets up a service's invocation environment, then invokes and returns
        an instance of the service.
        """
        request_string = dumps(request)
        instance = class_()
        worker_store = MagicMock()
        worker_store.worker_config = MagicMock
        worker_store.worker_config.outgoing_connections = MagicMock(return_value=(None, None, None))
        
        class_.update(instance, FakeServer(), None, worker_store, new_cid(), request, request_string, 
            simple_io_config={})

        def get_data(self, *ignored_args, **ignored_kwargs):
            return expected.get_data()

        instance.get_data = get_data
        instance.handle()
        
        return instance
