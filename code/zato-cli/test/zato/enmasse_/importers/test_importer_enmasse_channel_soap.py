# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from json import loads
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_soap import ChannelSOAPImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.odb.model import HTTPSOAP
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelSOAPFromYAML(TestCase):
    """ Tests importing SOAP channels from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = default_server_base_dir

        # Create a temporary file using the existing template which already contains SOAP channels
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize security and group importers (channels may use both)
        self.security_importer = SecurityImporter(self.importer)
        self.group_importer = GroupImporter(self.importer)
        self.importer.sec_defs = {} # Initialize sec_defs

        # Initialize the SOAP channel importer
        self.channel_soap_importer = ChannelSOAPImporter(self.importer)

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

        # Get the cluster instance from the database
        self.importer.cluster = self.importer.get_cluster(self.session)

        # Create security definitions first since SOAP channels may use them
        security_list = self.yaml_config['security']
        _ = self.security_importer.sync_security_definitions(security_list, self.session)

        # Create security groups since SOAP channels may be assigned to them
        group_list = self.yaml_config['groups']
        _, _ = self.group_importer.sync_groups(group_list, self.session)
        self.importer.group_defs = self.group_importer.group_defs

# ################################################################################################################################

    def test_channel_soap_creation(self):
        """ Test creating SOAP channels from YAML.
        """
        self._setup_test_environment()

        # Get SOAP channel definitions from YAML
        channel_soap_defs = self.yaml_config['channel_soap']

        # Process all SOAP channel definitions
        created, updated = self.channel_soap_importer.sync_channel_soap(channel_soap_defs, self.session)

        # Should have created all channels from the template
        self.assertEqual(len(created), 2)  # There are 2 SOAP channels in template_complex_01
        self.assertEqual(len(updated), 0)

        # Verify the SOAP channel was created correctly
        channel = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.channel.soap.1',
            connection=CONNECTION.CHANNEL,
            transport=URL_TYPE.SOAP
        ).one()

        self.assertEqual(channel.url_path, '/enmasse.soap.1')
        self.assertEqual(channel.soap_action, 'urn:enmasse:soap:1')
        self.assertEqual(channel.soap_version, '1.1')
        self.assertTrue(channel.is_active)
        self.assertFalse(channel.is_internal)
        self.assertIsNone(channel.security_id)

# ################################################################################################################################

    def test_channel_soap_creation_with_opaque_fields(self):
        """ Test that MTOM, security groups and rate limiting end up in the opaque attributes of a newly created channel.
        """
        self._setup_test_environment()

        channel_soap_defs = self.yaml_config['channel_soap']
        _ = self.channel_soap_importer.sync_channel_soap(channel_soap_defs, self.session)

        channel = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.channel.soap.2',
            connection=CONNECTION.CHANNEL,
            transport=URL_TYPE.SOAP
        ).one()

        # The column-level fields first ..
        self.assertEqual(channel.url_path, '/enmasse.soap.2')
        self.assertEqual(channel.soap_action, 'urn:enmasse:soap:2')
        self.assertEqual(channel.soap_version, '1.2')
        self.assertIsNotNone(channel.security_id)

        # .. and the fields carried in the opaque attributes.
        opaque = loads(channel.opaque1)

        self.assertTrue(opaque['use_mtom'])
        self.assertEqual(len(opaque['security_groups']), 2)
        self.assertEqual(len(opaque['rate_limiting']), 1)
        self.assertEqual(opaque['rate_limiting'][0]['cidr_list'], ['0.0.0.0/0'])

        # The template turns the audit log off for this channel
        self.assertIs(opaque['is_audit_log_active'], False)

        # The template configures response caching on this channel too
        response_cache = opaque['response_cache']
        self.assertIs(response_cache['is_enabled'], True)
        self.assertEqual(response_cache['ttl'], 2)
        self.assertEqual(response_cache['ttl_unit'], 'minutes')
        self.assertIs(response_cache['cache_on_second_request'], False)

        # A channel without the flag in YAML has it on
        channel_1 = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.channel.soap.1',
            connection=CONNECTION.CHANNEL,
            transport=URL_TYPE.SOAP
        ).one()

        opaque_1 = loads(channel_1.opaque1)
        self.assertIs(opaque_1['is_audit_log_active'], True)

# ################################################################################################################################

    def test_channel_soap_reimport_detects_no_changes(self):
        """ Test that importing the same YAML twice detects no changes the second time,
        including for the fields kept in the opaque attributes.
        """
        self._setup_test_environment()

        channel_soap_defs = self.yaml_config['channel_soap']

        created, updated = self.channel_soap_importer.sync_channel_soap(channel_soap_defs, self.session)
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # The second, identical import must be a no-op.
        created, updated = self.channel_soap_importer.sync_channel_soap(channel_soap_defs, self.session)
        self.assertEqual(len(created), 0)
        self.assertEqual(len(updated), 0)

# ################################################################################################################################

    def test_channel_soap_update(self):
        """ Test updating existing SOAP channels.
        """
        self._setup_test_environment()

        # First, get a SOAP channel definition from YAML and create it
        channel_soap_defs = self.yaml_config['channel_soap']
        channel_def = channel_soap_defs[0]  # Use the first definition

        # Create the SOAP channel
        instance = self.channel_soap_importer.create_channel_soap(channel_def, self.session)
        self.session.commit()
        self.assertEqual(instance.url_path, channel_def['url_path'])

        # Prepare an update definition based on the existing one
        update_def = {
            'name': channel_def['name'],
            'id': instance.id,
            'service': channel_def['service'],
            'url_path': '/enmasse.soap.1.updated',  # Changed path
            'soap_action': 'urn:enmasse:soap:1:updated',  # Changed SOAP action
            'soap_version': '1.2',  # Changed SOAP version
            'use_mtom': True,  # Turned on
        }

        # Update the SOAP channel
        updated_instance = self.channel_soap_importer.update_channel_soap(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.url_path, '/enmasse.soap.1.updated')
        self.assertEqual(updated_instance.soap_action, 'urn:enmasse:soap:1:updated')
        self.assertEqual(updated_instance.soap_version, '1.2')

        opaque = loads(updated_instance.opaque1)
        self.assertTrue(opaque['use_mtom'])

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.connection, CONNECTION.CHANNEL)
        self.assertEqual(updated_instance.transport, URL_TYPE.SOAP)

# ################################################################################################################################

    def test_complete_channel_soap_import_flow(self):
        """ Test the complete flow of importing SOAP channels from a YAML file.
        """
        self._setup_test_environment()

        # Process all SOAP channel definitions from the YAML
        channel_soap_list = self.yaml_config['channel_soap']
        channels_created, channels_updated = self.channel_soap_importer.sync_channel_soap(channel_soap_list, self.session)

        # Verify SOAP channels were created
        count = len(channel_soap_list)
        self.assertEqual(len(channels_created), count)
        self.assertEqual(len(channels_updated), 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
