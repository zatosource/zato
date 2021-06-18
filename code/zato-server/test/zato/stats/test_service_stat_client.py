# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test import rand_int, rand_string
from zato.common.events.client import Client as EventsClient
from zato.server.connection.stats import ServiceStatsClient

# ################################################################################################################################
# ################################################################################################################################

class TestImplClass(EventsClient):
    def __init__(self, host, port):
        # type: (str, int) -> None
        self.host = host
        self.port = port

        self.is_connect_called = False
        self.is_run_called     = False

# ################################################################################################################################

    def connect(self):
        self.is_connect_called = True

# ################################################################################################################################

    def run(self):
        self.is_run_called = True

# ################################################################################################################################
# ################################################################################################################################

class ServiceStatsClientTestCase(TestCase):

# ################################################################################################################################

    def test_init(self):

        host = rand_string()
        port = rand_int()

        stats_client = ServiceStatsClient(impl_class=TestImplClass)
        stats_client.init(host, port)

        self.assertTrue(stats_client.impl.is_connect_called)
        self.assertEqual(stats_client.host, host)
        self.assertEqual(stats_client.port, port)

# ################################################################################################################################

    def test_run(self):

        host = rand_string()
        port = rand_int()

        stats_client = ServiceStatsClient(impl_class=TestImplClass)

        stats_client.init(host, port)
        stats_client.run()

        self.assertTrue(stats_client.impl.is_run_called)

# ################################################################################################################################

    def xtest_push(self):
        pass

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
