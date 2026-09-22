# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from tempfile import NamedTemporaryFile
from unittest import TestCase, main

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.on_prem_gateway import OnPremGatewayImporter
from zato.common.crypto.api import CryptoManager
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# How many bits of randomness go into the suffix that keeps one run's names apart from
# another's
_Suffix_Bits = 32

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOnPremGateways(TestCase):
    """ Tests for importing on-premises gateways from YAML using enmasse.
    """

    def setUp(self) -> 'None':

        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file for YAML content
        contents = template_complex_01.encode('utf-8')

        self.temp_file = NamedTemporaryFile(delete=False, suffix='.yaml')
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
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def _get_suffix(self) -> 'str':
        """ What keeps the names of one run apart from the names of another.
        """
        out = CryptoManager.generate_hex_string(_Suffix_Bits)

        return out

# ################################################################################################################################

    def _get_gateway(self, suffix:'str') -> 'any_':
        """ Builds a gateway definition out of the first one in the fixture, under a name of its own.
        """
        gateways = self.yaml_config['on_prem_gateway']
        first = gateways[0]

        out = first.copy()
        out['name'] = f'enmasse.test_on_prem_gateway_{suffix}'
        out['hosts'] = [f'erp-db-{suffix}.corp.local:5432', f'crm-{suffix}.corp.local:443']

        return out

# ################################################################################################################################

    def test_sync_on_prem_gateways(self) -> 'None':
        """ Gateways are created on the first sync and updated in place on the second one.
        """
        self._setup_test_environment()

        suffix = self._get_suffix()
        gateway_defs = [self._get_gateway(suffix)]

        # First sync - should create the gateway
        created, updated = self.gateway_importer.sync_on_prem_gateways(gateway_defs, self.session)

        created_count = len(created)
        updated_count = len(updated)

        self.assertEqual(created_count, 1)
        self.assertEqual(updated_count, 0)

        gateway_name = gateway_defs[0]['name']

        self.assertIn(gateway_name, self.gateway_importer.gateway_defs)

        gateway_def = self.gateway_importer.gateway_defs[gateway_name]
        gateway_id = gateway_def['id']

        # Second sync - the gateway is updated in place and keeps its id
        created_2, updated_2 = self.gateway_importer.sync_on_prem_gateways(gateway_defs, self.session)

        created_count_2 = len(created_2)
        updated_count_2 = len(updated_2)

        self.assertEqual(created_count_2, 0)
        self.assertEqual(updated_count_2, 1)

        gateway_def_2 = self.gateway_importer.gateway_defs[gateway_name]
        gateway_id_2 = gateway_def_2['id']

        self.assertEqual(gateway_id, gateway_id_2)

# ################################################################################################################################

    def test_hosts_are_normalised(self) -> 'None':
        """ Addresses are trimmed and sorted.
        """
        self._setup_test_environment()

        suffix = self._get_suffix()

        gateway = self._get_gateway(suffix)
        gateway['hosts'] = ['  warehouse.corp.local:443  ', 'billing.corp.local:5432']

        hosts = self.gateway_importer.get_hosts(gateway)

        self.assertEqual(hosts, ['billing.corp.local:5432', 'warehouse.corp.local:443'])

# ################################################################################################################################

    def test_address_without_port_is_rejected(self) -> 'None':
        """ An address that is not host:port is refused.
        """
        self._setup_test_environment()

        suffix = self._get_suffix()

        gateway = self._get_gateway(suffix)
        gateway['hosts'] = ['erp-db.corp.local']

        with self.assertRaises(Exception):
            _ = self.gateway_importer.get_hosts(gateway)

# ################################################################################################################################

    def test_port_outside_range_is_rejected(self) -> 'None':
        """ A port outside the 1-65535 range is refused.
        """
        self._setup_test_environment()

        suffix = self._get_suffix()

        gateway = self._get_gateway(suffix)
        gateway['hosts'] = ['erp-db.corp.local:70000']

        with self.assertRaises(Exception):
            _ = self.gateway_importer.get_hosts(gateway)

# ################################################################################################################################

    def test_duplicate_address_within_a_gateway_is_rejected(self) -> 'None':
        """ The same address twice in one gateway is refused.
        """
        self._setup_test_environment()

        suffix = self._get_suffix()

        gateway = self._get_gateway(suffix)
        gateway['hosts'] = ['erp-db.corp.local:5432', 'erp-db.corp.local:5432']

        with self.assertRaises(Exception):
            _ = self.gateway_importer.get_hosts(gateway)

# ################################################################################################################################

    def test_same_address_in_two_gateways_is_rejected(self) -> 'None':
        """ One address belongs to one gateway.
        """
        self._setup_test_environment()

        suffix = self._get_suffix()

        first_suffix = f'{suffix}_a'
        second_suffix = f'{suffix}_b'

        first = self._get_gateway(first_suffix)
        second = self._get_gateway(second_suffix)

        shared = f'shared-{suffix}.corp.local:5432'
        first['hosts'] = [shared]
        second['hosts'] = [shared]

        gateway_defs = [first, second]

        with self.assertRaises(Exception):
            _ = self.gateway_importer.sync_on_prem_gateways(gateway_defs, self.session)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    # Configure logging for tests
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Run tests
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
