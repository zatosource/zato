# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# nose
from nose.tools import eq_

# Paste
from paste.util.converters import asbool

# live test case
from . import LiveTestCase

# SIO live test services
from . import zato_test_sio_live

class SIOLiveTestCase(LiveTestCase):

    SERVICES_SOURCE = 'zato_test_sio_live.py'

    def _run_tests_output_assigned_manually(self, service_name, service_class):

        # No input provided hence we expect a proper message on output
        try:
            response = self.invoke_asi(service_name)
        except Exception as e:
            self.assertIn('Missing input', e.message)

        test_data = service_class.test_data

# ################################################################################################################################

        # JSON request/response over AnyServiceInvoker
        response = self.invoke_asi(service_name, test_data)
        service_class.check_json(response.response, False)

# ################################################################################################################################

        # JSON request/response over JSONClient
        response = self.invoke_json(
            self.set_up_client_and_channel(service_name, 'json', 'plain_http'), test_data)
        service_class.check_json(response.response, False)

# ################################################################################################################################

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

        for request_wrapper, xpath_string_pattern, transport in self.get_xml_soap_config():

            # XML request/response over XMLClient
            client = self.set_up_client_and_channel(service_name, 'xml', transport)
            response = self.invoke_xml(client, request_wrapper.format(request).encode('utf-8'))

            for name in('should_as_is', 'is_boolean', 'should_boolean', 'csv1', 'float', 'integer', 'integer2',
                        'unicode1', 'unicode2', 'utc'):

                expected = test_data[name]
                actual = self.get_xml_value_from_response(xpath_string_pattern, response, name)

                if name in ('is_boolean', 'should_boolean'):
                    expected = asbool(expected)

                if name == 'float':
                    expected = float(expected)

                if name in ('integer', 'integer2'):
                    expected = int(expected)

                if name == 'utc':
                    expected = expected.replace('+00:00', '')

                eq_(actual, expected, 'name:`{}` actual:`{}` expected:`{}`'.format(name, repr(actual), repr(expected)))

# ################################################################################################################################

    def test_channels_output_assigned_manually(self):
        if not self.should_run:
            return

        service_data = (
            ('zato-test-sio-live.roundtrip', zato_test_sio_live.Roundtrip),
            ('zato-test-sio-live.from-dict', zato_test_sio_live.FromDict),
        )

        for service_info in service_data:
            self._run_tests_output_assigned_manually(*service_info)

# ################################################################################################################################

    def test_channels_output_from_sqlalchemy(self):
        if not self.should_run:
            return

        service_name = 'zato-test-sio-live.from-sql-alchemy'

        expected = [
            ('impl_name', 'zato.server.service.internal.Ping'),
            ('is_active', True),
            ('is_internal', True),
            ('name', 'zato.ping'),
            ('slow_threshold', 99999)
        ]

# ################################################################################################################################

        # JSON request/response over AnyServiceInvoker

        response = self.invoke_asi(service_name, {})
        eq_(sorted(response.response.items()), expected)

# ################################################################################################################################

        # JSON request/response over JSONClient
        response = self.invoke_json(self.set_up_client_and_channel(service_name, 'json', 'plain_http'), {})
        eq_(sorted(response.response.items()), expected)

# ################################################################################################################################

        for request_wrapper, xpath_string_pattern, transport in self.get_xml_soap_config():

            # XML request/response over XMLClient
            client = self.set_up_client_and_channel(service_name, 'xml', transport)
            response = self.invoke_xml(client, request_wrapper.format('<dummy/>').encode('utf-8'))

            actual_items = {}

            for name in ('name', 'is_active', 'impl_name', 'is_internal', 'slow_threshold'):
                actual_items[name] = self.get_xml_value_from_response(xpath_string_pattern, response, name)

            eq_(sorted(actual_items.items()), expected)

# ################################################################################################################################
