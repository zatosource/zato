# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import glob, os, shutil, time
from unittest import TestCase

# Bunch
from bunch import bunchify

# configobj
from configobj import ConfigObj

# nose
from nose.tools import eq_

# Zato
from zato.cli.util import Util
from zato.client import JSONClient, XMLClient
from zato.common.util import new_cid

DEV_CONFIG_FILE = os.path.expanduser(os.path.sep.join(['~', '.zato', 'dev.ini']))
SERVER_CONFIG_FILE = os.path.sep.join(['config', 'repo', 'server.conf'])
URL_PATH_PATTERN = '/zato/test-live/{}/{}'

class LiveTestCase(TestCase):

    SERVICES_SOURCE = 'zato_test_live.py' # to be overridden in children classes

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

            test_pattern = os.path.join(os.path.dirname(__file__), self.SERVICES_SOURCE)
            for item in glob.glob(test_pattern):
                shutil.copy(item, pickup_dir)

            # Needed because uploading a package is asynchronous so we don't want to run the tests
            # until the package is ready.
            # TODO: do not wait a fixed amount of time but rather check (every second?) if the service has already been already deployed
            time.sleep(1)

            self.should_run = True

    def tearDown(self):
        """ Do away with all the test services and objects possibly created earlier.
        """
        if self.should_run:
            for item in self.util.client.invoke(
                    'zato.service.get-list', {'cluster_id': self.util.client.cluster_id, 'name_filter': 'zato-test-live'}):
                self.util.client.invoke('zato.service.delete', {'id': item['id']})

        self.util = None

    def set_up_client_and_channel(self, service, data_format, transport):
        path = URL_PATH_PATTERN.format(service, new_cid())
        self.util.client.invoke('zato.http-soap.create', {
            'cluster_id': self.util.client.cluster_id,
            'name': path,
            'is_active': True,
            'connection': 'channel',
            'transport': transport,
            'is_internal': True,
            'url_path': path,
            'service': service,
            'security_id': None,
            'data_format': data_format
        })

        if data_format == 'json':
            client_class = JSONClient
        else:
            client_class = XMLClient

        return client_class(self.util.client.address, path)

# ################################################################################################################################

    def get_xml_soap_config(self):

        # Plain XML config
        request_wrapper_plain_xml = '{}'
        xpath_string_pattern_plain_xml = '//{}'
        transport_plain_xml = 'plain_http'

        # SOAP 1.1 config
        request_wrapper_soap_11 = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>{}</soap:Body>
            </soap:Envelope>
        """
        xpath_string_pattern_soap_11 = "//*[local-name()='{}']"
        transport_soap_11 = 'soap'

        return [
            [request_wrapper_plain_xml, xpath_string_pattern_plain_xml, transport_plain_xml],
            [request_wrapper_soap_11, xpath_string_pattern_soap_11, transport_soap_11],
        ]

    def get_xml_value_from_response(self, xpath_string_pattern, response, name):
        expr = xpath_string_pattern.format(name)
        actual = response.xpath(expr)

        if not actual:
            raise Exception('Could not find {} in {}'.format(expr, etree.tostring(response, pretty_print=True)))
        else:
            return actual[0]

    def _invoke(self, client, unserialize_func, service=None, request=None):
        """ Invokes a service using AnyServiceInvoker.
        """
        request = request or {}
        if service:
            response = client.invoke(service, request)
        else:
            response = client.invoke(request)

        if response.ok:
            if not response.data:
                raise Exception('No response.data in {}'.format(response))

            return unserialize_func(response.data)
        else:
            raise Exception(response.details)

    def invoke_asi(self, service, request=None):
        """ Invokes a service using AnyServiceInvoker.
        """
        return self._invoke(self.util.client, bunchify, service, request)

    def invoke_json(self, client, request=None):
        """ Invokes a service using JSONClient.
        """
        return self._invoke(client, bunchify, request)

    def invoke_xml(self, client, request=None):
        """ Invokes a service using XMLClient.
        """
        return self._invoke(client, bunchify, request)
