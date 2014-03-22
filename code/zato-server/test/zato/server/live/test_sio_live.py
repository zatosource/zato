# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import glob, os, shutil, time
from json import dumps, loads
from logging import getLogger
from unittest import TestCase

# Bunch
from bunch import Bunch, bunchify

# configobj
from configobj import ConfigObj

# etree
from lxml import etree

# nose
from nose.tools import eq_

# Paste
from paste.util.converters import asbool

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

logger = getLogger(__name__)

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

            return bunchify(response.data)
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

# ################################################################################################################################

    def _run_tests_output_assigned_manually(self, service_name, service_class):

        # No input provided hence we expect a proper message on output
        try:
            response = self.invoke_asi(service_name)
        except Exception, e:
            self.assertIn('Missing input', e.message)

        test_data = service_class.test_data

        # ########################################################################################################################

        # JSON request/response over AnyServiceInvoker
        response = self.invoke_asi(service_name, test_data)
        service_class.check_json(response.response, False)

        # ########################################################################################################################

        # JSON request/response over JSONClient
        response = self.invoke_json(
            self.set_up_client_and_channel(service_name, 'json', 'plain_http'), test_data)
        service_class.check_json(response.response, False)

        # ########################################################################################################################

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

        config = [
            [request_wrapper_plain_xml, xpath_string_pattern_plain_xml, transport_plain_xml],
            [request_wrapper_soap_11, xpath_string_pattern_soap_11, transport_soap_11],
        ]

        request = """<request>
                    <should_as_is>True</should_as_is>
                    <is_boolean>True</is_boolean>
                    <should_boolean>False</should_boolean>
                    <csv1>1,2,3,4</csv1>
                    <dict>
                     <item><key>a</key><value>b</value></item>
                     <item><key>c</key><value>d</value></item>
                    </dict>
                    <float>2.3</float>
                    <integer>190</integer>
                    <integer2>0</integer2>
                    <list>
                     <item>1</item>
                     <item>2</item>
                     <item>3</item>
                    </list>

                    <list_of_dicts>

                     <item_dict>
                      <item>
                        <key>1</key>
                        <value>11</value>
                      </item>
                      <item>
                        <key>2</key>
                        <value>22</value>
                      </item>
                     </item_dict>

                     <item_dict>
                      <item>
                        <key>3</key>
                        <value>33</value>
                      </item>
                     </item_dict>

                     <item_dict>
                      <item>
                        <key>4</key>
                        <value>44</value>
                      </item>
                      <item>
                        <key>5</key>
                        <value>55</value>
                      </item>
                      <item>
                        <key>3</key>
                        <value>33</value>
                      </item>
                      <item>
                        <key>2</key>
                        <value>22</value>
                      </item>
                      <item>
                        <key>1</key>
                        <value>11</value>
                      </item>
                     </item_dict>

                    </list_of_dicts>

                    <unicode1>zzzä</unicode1>
                    <unicode2>zä</unicode2>
                    <utc>2012-01-12T03:12:19+00:00</utc>
                </request>"""


        for request_wrapper, xpath_string_pattern, transport in config:

            # XML request/response over XMLClient
            client = self.set_up_client_and_channel(service_name, 'xml', transport)

            response = self.invoke_xml(client, request_wrapper.format(request).encode('utf-8'))

            for name in('should_as_is', 'is_boolean', 'should_boolean', 'csv1', 'float', 'integer', 'integer2',\
                        'unicode1', 'unicode2', 'utc'):
                expr = xpath_string_pattern.format(name)

                actual = response.xpath(expr)
                if not actual:
                    raise Exception('Could not find {} in {}'.format(expr, etree.tostring(response, pretty_print=True)))
                else:
                    actual = actual[0]

                expected = test_data[name]

                if name in ('is_boolean', 'should_boolean'):
                    expected = asbool(expected)

                if name == 'float':
                    expected = float(expected)

                if name in ('integer', 'integer2'):
                    expected = int(expected)

                if name == 'utc':
                    expected = expected.replace('+00:00', '')

                eq_(actual, expected, 'name:`{}` actual:`{}` expected:`{}`'.format(name, repr(actual), repr(expected)))

        # ########################################################################################################################

    def test_channels_output_assigned_manually(self):
        if not self.should_run:
            return

        service_data = (
            ('zato-test-live-sio.roundtrip', zato_test_live_sio.Roundtrip),
            ('zato-test-live-sio.from-dict', zato_test_live_sio.FromDict),
            ('zato-test-live-sio.passthrough-to-roundtrip', zato_test_live_sio.PassthroughToRoundtrip),
            ('zato-test-live-sio.passthrough-to-from-dict', zato_test_live_sio.PassthroughToFromDict),
        )

        for service_info in service_data:
            self._run_tests_output_assigned_manually(*service_info)
