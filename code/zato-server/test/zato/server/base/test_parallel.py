# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
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
