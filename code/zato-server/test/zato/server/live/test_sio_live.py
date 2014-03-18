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
from zato.client import JSONClient, SOAPClient, XMLClient
from zato.common import ZatoException
from zato.common.test import rand_bool, rand_string
from zato.common.util import new_cid
from zato.server.service import Bool, Dict, Nested
from zato.server.service.reqresp.sio import ValidationException

# Zato - test services
from . import zato_test_live_sio 

DEV_CONFIG_FILE = os.path.expanduser(os.path.sep.join(['~', '.zato', 'dev.ini']))
SERVER_CONFIG_FILE = os.path.sep.join(['config', 'repo', 'server.conf'])
URL_PATH_PATTERN = '/zato/test-live/{}/{}'

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

    def set_up_client_and_channel_json(self, service):
        path = URL_PATH_PATTERN.format(service, new_cid())
        self.util.client.invoke('zato.http-soap.create', {
            'cluster_id': self.util.client.cluster_id,
            'name': path,
            'is_active': True,
            'connection': 'channel',
            'transport': 'plain_http',
            'is_internal': True,
            'url_path': path,
            'service': service,
            'security_id': None,
            'data_format': 'json'
        })
        return JSONClient(self.util.client.address, path)

    def invoke_asi(self, service, request=None):
        """ Invokes a service using AnyServiceInvoker.
        """
        request = request or {}
        response = self.util.client.invoke(service, request)

        if response.ok:
            return bunchify(response.data)
        else:
            raise Exception(response.details)

    def invoke_json(self, client, request=None):
        """ Invokes a service using JSONClient.
        """
        request = request or {}
        response = client.invoke(request)

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
            response = self.invoke_asi(service)
        except Exception, e:
            self.assertIn('Missing input', e.message)

        # JSON request/response over AnyServiceInvoker
        response = self.invoke_asi(service, zato_test_live_sio.TestSimpleTypes.test_data)
        zato_test_live_sio.TestSimpleTypes.test_json(response.response, False)

        # JSON request/response over JSONClient
        response = self.invoke_json(self.set_up_client_and_channel_json(service), zato_test_live_sio.TestSimpleTypes.test_data)
        zato_test_live_sio.TestSimpleTypes.test_json(response.response, False)