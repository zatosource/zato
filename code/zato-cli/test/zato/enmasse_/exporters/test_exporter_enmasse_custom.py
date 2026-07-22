# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from unittest import TestCase, main

# PyYAML
import yaml

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.util import FileWriter
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# Definitions of two custom connector types, as their authors would keep them in an enmasse file.
template_custom_connectors = """
custom_crm:
  - name: enmasse.custom.crm.1
    host: 127.0.0.1
    port: 9950
    api_key: enmasse-api-key-1
  - name: enmasse.custom.crm.2
    host: 10.152.81.19
    api_key: enmasse-api-key-2

custom_billing:
  - name: enmasse.custom.billing.1
    address: https://billing.example.com
    is_sandbox: true
"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseCustomConnectorsExport(TestCase):
    """ Tests exporting custom connector definitions to YAML using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file with the definitions of the custom connector types
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_custom_connectors.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer and the exporter
        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session, parsing the YAML file
        and importing everything the file contains.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)
            _ = self.importer.sync_from_yaml(self.yaml_config, self.session)

# ################################################################################################################################

    def test_custom_export(self):
        """ Test exporting custom connector definitions to a dictionary.
        """
        self._setup_test_environment()

        # Export everything there is
        exported = self.exporter.export_to_dict(self.session)

        # Both types should be present, each under its own top-level key
        self.assertIn('custom_crm', exported)
        self.assertIn('custom_billing', exported)

        # Index the crm definitions by name
        crm_by_name = {item['name']: item for item in exported['custom_crm']}

        self.assertIn('enmasse.custom.crm.1', crm_by_name)
        self.assertIn('enmasse.custom.crm.2', crm_by_name)

        # The declared fields must survive the round trip along with their types
        crm_1 = crm_by_name['enmasse.custom.crm.1']

        self.assertEqual(crm_1['host'], '127.0.0.1')
        self.assertEqual(crm_1['port'], 9950)
        self.assertEqual(crm_1['api_key'], 'enmasse-api-key-1')

        # The billing type carries its own fields
        billing_by_name = {item['name']: item for item in exported['custom_billing']}
        billing_1 = billing_by_name['enmasse.custom.billing.1']

        self.assertEqual(billing_1['address'], 'https://billing.example.com')
        self.assertTrue(billing_1['is_sandbox'])

# ################################################################################################################################

    def test_custom_export_file_round_trip(self):
        """ Test that an exported file can be read back with the custom connector sections intact.
        """
        self._setup_test_environment()

        # Export everything there is ..
        exported = self.exporter.export_to_dict(self.session)

        # .. write it out the way the enmasse command does ..
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        output_file.close()

        try:
            writer = FileWriter(output_file.name)
            writer.write(exported)

            # .. and read it back as YAML.
            with open(output_file.name, 'r') as f:
                round_trip = yaml.safe_load(f.read())

        finally:
            os.unlink(output_file.name)

        # The custom sections must have survived the file round trip
        self.assertIn('custom_crm', round_trip)
        self.assertIn('custom_billing', round_trip)

        crm_by_name = {item['name']: item for item in round_trip['custom_crm']}
        crm_1 = crm_by_name['enmasse.custom.crm.1']

        self.assertEqual(crm_1['host'], '127.0.0.1')
        self.assertEqual(crm_1['port'], 9950)
        self.assertEqual(crm_1['api_key'], 'enmasse-api-key-1')

        billing_by_name = {item['name']: item for item in round_trip['custom_billing']}
        billing_1 = billing_by_name['enmasse.custom.billing.1']

        self.assertEqual(billing_1['address'], 'https://billing.example.com')
        self.assertTrue(billing_1['is_sandbox'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
