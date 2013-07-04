# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# bunch
from bunch import Bunch

# nose
from nose.tools import eq_

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

class _FakeSession(object):
    def __init__(self, *ignored, **kwargs):
        self.pool_size = kwargs.get('pool_maxsize', 'missing')
        self.request_args = None
        self.request_kwargs = None
        
    def request(self, *args, **kwargs):
        self.request_args = args
        self.request_kwargs = kwargs
        
        return Bunch({'status_code':rand_string()})
        
class _FakeRequestsModule(object):
    def __init__(self):
        self.session_obj = None
        
    def session(self, *args, **kwargs):
        self.session_obj = _FakeSession(*args, **kwargs)
        return self.session_obj

class PingTestCase(TestCase):
    
    def test_ping_method(self):
        """ https://github.com/zatosource/zato/issues/44 (outconn HTTP/SOAP ping method)
        """
        expected_ping_method = 'ping-{}'.format(rand_string())
        requests_module = _FakeRequestsModule()
        
        config = {'sec_type':rand_string(), 'address':rand_string(), 
                  'ping_method':expected_ping_method, 'pool_size':rand_int()}
        
        wrapper = HTTPSOAPWrapper(config, requests_module)
        wrapper.ping(rand_string())
        
        ping_method = requests_module.session_obj.request_args[0]
        eq_(expected_ping_method, ping_method)

    def test_pool_size(self):
        """ https://github.com/zatosource/zato/issues/77 (outconn HTTP/SOAP pool size)
        """
        expected_pool_size = rand_int()
        requests_module = _FakeRequestsModule()
        
        config = {'sec_type':rand_string(), 'address':rand_string(), 
                  'ping_method':rand_string(), 'pool_size':expected_pool_size}
        
        wrapper = HTTPSOAPWrapper(config, requests_module)
        wrapper.ping(rand_string())
        
        eq_(expected_pool_size, requests_module.session_obj.pool_size)
