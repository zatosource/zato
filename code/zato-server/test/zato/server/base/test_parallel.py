# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from hashlib import sha1
from unittest import TestCase

# Bunch
from bunch import Bunch

# mock
from mock import patch

# nose
from nose.tools import eq_, ok_

# Zato
from zato.common import CHANNEL
from zato.common.broker_message import SERVICE
from zato.common.test import rand_string
from zato.server.base.parallel import ParallelServer

class ParallelServerTestCase(TestCase):
    def test_startup_services(self):

        class FakeBrokerClient(object):
            def __init__(self):
                self.messages = {}
                
            def invoke_async(self, msg):
                self.messages[msg['service']] = msg
                
        broker_client = FakeBrokerClient()
        
        startup_services = Bunch()
        for x in range(10):
            name =  rand_string()
            payload = rand_string()
            startup_services[name] = payload
        
        ps = ParallelServer()
        ps.broker_client = broker_client
        ps.fs_server_config = Bunch()
        ps.fs_server_config.startup_services = startup_services
        
        ps.invoke_startup_services()
        
        for expected_service, expected_payload in startup_services.items():
            msg = Bunch(broker_client.messages[expected_service])
            eq_(msg.action, SERVICE.PUBLISH)
            eq_(msg.channel, CHANNEL.STARTUP_SERVICE)
            eq_(msg.payload, expected_payload)
            eq_(msg.service, expected_service)
            ok_(msg.cid.startswith('K'))
            self.assertEquals(len(msg.cid), 40)
            
    def test_set_tls_info(self):

        expected_cert_dict = rand_string()
        expected_cert_der = rand_string()
        expected_cert_sha1 = sha1(expected_cert_der).hexdigest().upper()
            
        class FakeRequestDispatcher(object):
            def dispatch(self, *ignored_args, **ignored_kwargs):
                return rand_string()
            
        class FakeWorkerStore(object):
            request_dispatcher = FakeRequestDispatcher()
            
        class FakeGunicornSocket(object):
            def getpeercert(self, needs_der=False):
                if needs_der:
                    return expected_cert_der
                return expected_cert_dict
            
        def start_response(*ignored_args, **ignored_kwargs):
            pass
        
        for wsgi_url_scheme in('https', 'http'):
            wsgi_environ = {
                'wsgi.url_scheme': wsgi_url_scheme,
                'gunicorn.socket': FakeGunicornSocket(),
                'zato.http.response.status': rand_string()
            }
    
            ps = ParallelServer()
            ps.worker_store = FakeWorkerStore()
            ps.on_wsgi_request(wsgi_environ, start_response)
            
            if wsgi_url_scheme == 'https':
                eq_(wsgi_environ['zato.tls.client_cert.dict'], expected_cert_dict)
                eq_(wsgi_environ['zato.tls.client_cert.der'], expected_cert_der)
                eq_(wsgi_environ['zato.tls.client_cert.sha1'], expected_cert_sha1)
            else:
                self.assertTrue('zato.tls.client_cert.dict' not in wsgi_environ)
                self.assertTrue('zato.tls.client_cert.der' not in wsgi_environ)
                self.assertTrue('zato.tls.client_cert.sha1' not in wsgi_environ)
