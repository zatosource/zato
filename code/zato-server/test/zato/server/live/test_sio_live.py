# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import glob, os, shutil, time
from json import dumps, loads
from unittest import TestCase

# Bunch
from bunch import Bunch, bunchify

# configobj
from configobj import ConfigObj

# nose
from nose.tools import eq_

# Zato
from zato.cli.util import Util
from zato.common import ZatoException
from zato.common.test import rand_bool, rand_string
from zato.server.service import Bool, Dict, Nested
from zato.server.service.reqresp.sio import ValidationException

# Zato - test services
from . import zato_test_live_sio 

DEV_CONFIG_FILE = os.path.expanduser(os.path.sep.join(['~', '.zato', 'dev.ini']))
SERVER_CONFIG_FILE = os.path.sep.join(['config', 'repo', 'server.conf'])

class SIOLiveTestCase(TestCase):

    def setUp(self):
        """ If it's a development environment, set up the client and deploy test services + objects.
        """
        self.should_run = False

        # Run the tests only if it's a development box
        if os.path.exists(DEV_CONFIG_FILE):
            config = ConfigObj(DEV_CONFIG_FILE)

            server_fs_loc = os.path.expanduser(config['server1']['fs_location'])
            pickup_dir = os.path.join(server_fs_loc, 'pickup-dir')

            self.util = Util(server_fs_loc)
            self.util.set_zato_client()

            test_pattern = os.path.join(os.path.dirname(__file__), 'zato_test_live_*')
            for item in glob.glob(test_pattern):
                shutil.copy(item, pickup_dir)

            # Needed because uploading a package is asynchronous so we don't want to run the tests
            # until the package is ready.
            time.sleep(0.2)

            self.should_run = True

    def tearDown(self):
        """ Do away with all the test services and objects possibly created earlier.
        """
        for item in self.util.client.invoke(
                'zato.service.get-list', {'cluster_id': self.util.client.cluster_id, 'name_filter': 'zato-test-live'}):
            self.util.client.invoke('zato.service.delete', {'id': item['id']})

        self.util = None

    def invoke(self, service, request=None):
        request = request or {}
        response = self.util.client.invoke(service, request)

        if response.ok:
            return bunchify(response.data)
        else:
            raise Exception(response.details)

    def test_simple_types(self):
        if not self.should_run:
            return

        service = 'zato-test-live-sio.test-simple-types'

        # No input provided hence we expect a proper message on output
        try:
            response = self.invoke(service)
        except Exception, e:
            self.assertIn('Input required yet not provided', e.message)

        # JSON request/response
        response = self.invoke(service, zato_test_live_sio.TestSimpleTypes.test_data)
        zato_test_live_sio.TestSimpleTypes.test_json(response.response, False)