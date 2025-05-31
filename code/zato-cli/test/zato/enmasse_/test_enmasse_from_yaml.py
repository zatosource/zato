# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.channel import ChannelImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseFromYAML(TestCase):
    """ Tests importing configuration from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file for YAML content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize specialized importers
        self.security_importer = SecurityImporter(self.importer)
        self.channel_importer = ChannelImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_yaml_parsing(self):
        """ Test that the YAML file is parsed correctly.
        """
        self._setup_test_environment()

        # Verify the YAML was parsed correctly
        self.assertIn('security', self.yaml_config)
        self.assertIsInstance(self.yaml_config['security'], list)
        self.assertIn('channel_rest', self.yaml_config)
        self.assertIsInstance(self.yaml_config['channel_rest'], list)
        self.assertIn('outgoing_rest', self.yaml_config)
        self.assertIsInstance(self.yaml_config['outgoing_rest'], list)
        self.assertIn('scheduler', self.yaml_config)
        self.assertIsInstance(self.yaml_config['scheduler'], list)

# ################################################################################################################################

    def test_channel_rest_creation(self):
        """ Test the creation of REST channels.
        """
        self._setup_test_environment()

        # First process security definitions which channels depend on
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)



        # Filter only REST channel definitions
        channel_defs = self.yaml_config['channel_rest']
        self.assertTrue(len(channel_defs) > 0, 'No REST channel definitions found in YAML')

        # Process channel definitions
        channels_created, _ = self.channel_importer.sync_channel_rest(channel_defs, self.session)

        # Assert the correct number of items were created
        self.assertEqual(len(channels_created), len(channel_defs), 'Not all REST channels were created')

        # Verify specific channels were created correctly
        for channel in channels_created:
            self.assertTrue(channel.name.startswith('enmasse.channel.rest.'))
            self.assertTrue(channel.url_path.startswith('/enmasse.rest.'))
            self.assertEqual(channel.connection, 'channel')
            self.assertEqual(channel.transport, 'plain_http')

            # Check for channel with security
            if channel.name == 'enmasse.channel.rest.3':
                # Verify that security was configured properly
                # Find the channel definition in YAML using a loop
                channel_def = None
                for c in channel_defs:
                    if c['name'] == channel.name:
                        channel_def = c
                        break

                self.assertIsNotNone(channel_def, f'Channel definition not found for {channel.name}')
                self.assertIn('security', channel_def, 'Channel should have security defined in YAML') # type: ignore

                # Ensure the security name in YAML exists in the importer's security definitions
                security_name = channel_def['security'] # type: ignore
                self.assertIn(security_name, self.importer.sec_defs, f'Security definition {security_name} not found')

            # Check for channel with data_format
            if channel.name in ['enmasse.channel.rest.2', 'enmasse.channel.rest.3']:
                self.assertEqual(channel.data_format, 'json', f'Wrong data_format for {channel.name}')

# ################################################################################################################################

    def test_outgoing_rest_configuration(self):
        """ Test the configuration of outgoing REST connections.
        """
        self._setup_test_environment()

        # Verify outgoing_rest configurations exist in the YAML
        outgoing_defs = self.yaml_config['outgoing_rest']
        self.assertTrue(len(outgoing_defs) > 0, 'No outgoing REST definitions found in YAML')

        # Check specific properties in the outgoing connections
        for item in outgoing_defs:
            self.assertIn('name', item)
            self.assertIn('host', item)
            self.assertIn('url_path', item)
            self.assertTrue(item['name'].startswith('enmasse.outgoing.rest.'))

        # Verify the specific details for each connection
        conn1 = cast_('any_', None)
        conn2 = cast_('any_', None)
        conn5 = cast_('any_', None)

        # Find connections by name using a simple loop
        for item in outgoing_defs:
            if item['name'] == 'enmasse.outgoing.rest.1':
                conn1 = item
            elif item['name'] == 'enmasse.outgoing.rest.2':
                conn2 = item
            elif item['name'] == 'enmasse.outgoing.rest.5':
                conn5 = item

        # Check conn1 details
        self.assertIsNotNone(conn1)
        self.assertEqual(conn1['host'], 'https://example.com:443')
        self.assertEqual(conn1['url_path'], '/sso/{type}/hello/{endpoint}')
        self.assertEqual(conn1['data_format'], 'json')
        self.assertEqual(conn1['timeout'], 60)

        # Check conn2 security configuration
        self.assertIsNotNone(conn2)
        self.assertIn('security', conn2)
        self.assertEqual(conn2['security'], 'enmasse.bearer_token.1')

        # Check conn5 TLS verification setting
        self.assertIsNotNone(conn5)
        self.assertIn('tls_verify', conn5)
        self.assertEqual(conn5['tls_verify'], False)

# ################################################################################################################################

    def test_scheduler_configuration(self):
        """ Test the configuration of scheduled jobs.
        """
        self._setup_test_environment()

        # Verify scheduler configurations exist in the YAML
        scheduler_defs = self.yaml_config['scheduler']
        self.assertTrue(len(scheduler_defs) > 0, 'No scheduler definitions found in YAML')

        # Check common properties for all scheduler items
        for item in scheduler_defs:
            self.assertIn('name', item)
            self.assertIn('service', item)
            self.assertIn('job_type', item)
            self.assertIn('start_date', item)
            self.assertTrue(item['name'].startswith('enmasse.scheduler.'))
            self.assertEqual(item['service'], 'demo.ping')
            self.assertEqual(item['job_type'], 'interval_based')

        # Verify different interval types (seconds, minutes, hours, days)
        scheduler1 = cast_('any_', None)
        scheduler2 = cast_('any_', None)
        scheduler3 = cast_('any_', None)
        scheduler4 = cast_('any_', None)

        # Find scheduler items by name using a simple loop
        for item in scheduler_defs:
            if item['name'] == 'enmasse.scheduler.1':
                scheduler1 = item
            elif item['name'] == 'enmasse.scheduler.2':
                scheduler2 = item
            elif item['name'] == 'enmasse.scheduler.3':
                scheduler3 = item
            elif item['name'] == 'enmasse.scheduler.4':
                scheduler4 = item

        # Check scheduler with seconds interval
        self.assertIsNotNone(scheduler1)
        self.assertIn('seconds', scheduler1)
        self.assertEqual(scheduler1['seconds'], 2)

        # Check scheduler with minutes interval
        self.assertIsNotNone(scheduler2)
        self.assertIn('minutes', scheduler2)
        self.assertEqual(scheduler2['minutes'], 51)

        # Check scheduler with hours interval
        self.assertIsNotNone(scheduler3)
        self.assertIn('hours', scheduler3)
        self.assertEqual(scheduler3['hours'], 3)

        # Check scheduler with days interval
        self.assertIsNotNone(scheduler4)
        self.assertIn('days', scheduler4)
        self.assertEqual(scheduler4['days'], 10)

# ################################################################################################################################

    def test_complete_import_flow(self):
        """ Test the complete flow of importing all definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process security definitions
        security_list = self.yaml_config.get('security', [])
        _ = self.security_importer.sync_security_definitions(security_list, self.session)

        # Process channels which depend on security definitions
        channel_list = self.yaml_config.get('channel_rest', [])
        _ = self.channel_importer.sync_channel_rest(channel_list, self.session)

        # Verify security definitions were created
        self.assertTrue(len(self.importer.sec_defs) >= 5, 'Not all security definitions were created')

        # Check each security definition type exists
        security_types = [def_info['type'] for def_info in self.importer.sec_defs.values()]
        self.assertIn('basic_auth', security_types)
        self.assertIn('bearer_token', security_types)
        self.assertIn('ntlm', security_types)
        self.assertIn('apikey', security_types)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
