# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
import tempfile
from unittest import TestCase, main

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.on_prem_gateway import OnPremGatewayImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The section of the file the gateways live in
_Section = 'on_prem_gateway'

# The prefix the fixture's own gateways go by
_Name_Prefix = 'enmasse.'

# Everything an exported gateway carries
_Exported_Keys = ['hosts', 'is_active', 'name']

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOnPremGatewayExporter(TestCase):
    """ Tests exporting on-premises gateway definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':

        environment = get_shared_environment()
        self.server_path = environment.server_dir

        contents = template_complex_01.encode('utf-8')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(contents)
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.gateway_importer = OnPremGatewayImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':

        if self.session:
            self.session.close()

        os.unlink(self.temp_file.name)

        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        _ = self.importer.get_cluster(self.session)

        gateways_from_yaml = self.yaml_config[_Section]
        _, _ = self.gateway_importer.sync_on_prem_gateways(gateways_from_yaml, self.session)

        self.session.commit()

# ################################################################################################################################

    def _get_exported_gateways(self) -> 'any_':
        """ Exports everything and returns the gateways the fixture put in.
        """
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        # Our response to produce
        out = []

        for item in exported_data[_Section]:

            name = item['name']

            if name.startswith(_Name_Prefix):
                out.append(item)

        return out

# ################################################################################################################################

    def test_on_prem_gateway_export(self) -> 'None':
        """ Tests the export of on-premises gateway definitions.
        """
        self._setup_test_environment()

        exported_gateways = self._get_exported_gateways()
        expected_gateways = self.yaml_config[_Section]

        exported_count = len(exported_gateways)
        expected_count = len(expected_gateways)

        self.assertEqual(exported_count, expected_count,
            f'Expected {expected_count} gateways, but got {exported_count}')

        exported_by_name = {}

        for item in exported_gateways:
            exported_by_name[item['name']] = item

        for expected_gateway in expected_gateways:

            expected_name = expected_gateway['name']

            self.assertIn(expected_name, exported_by_name, f'Exported gateways missing: {expected_name}')

            exported_gateway = exported_by_name[expected_name]
            expected_hosts = sorted(expected_gateway['hosts'])

            self.assertEqual(exported_gateway['name'], expected_name)
            self.assertEqual(exported_gateway['is_active'], expected_gateway['is_active'])

            # The importer sorts the addresses
            self.assertEqual(exported_gateway['hosts'], expected_hosts)

# ################################################################################################################################

    def test_an_exported_gateway_carries_the_configuration_only(self) -> 'None':
        """ A name, a flag and a list of addresses, and nothing else.
        """
        self._setup_test_environment()

        exported_gateways = self._get_exported_gateways()

        for item in exported_gateways:

            keys = sorted(item.keys())

            self.assertEqual(keys, _Exported_Keys)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
