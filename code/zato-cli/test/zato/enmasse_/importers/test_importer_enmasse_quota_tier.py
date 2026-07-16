# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from tempfile import NamedTemporaryFile
from unittest import TestCase, main
import uuid

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.quota_tier import QuotaTierImporter
from zato.cli.enmasse.importers.security import SecurityImporter
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

class TestEnmasseQuotaTiers(TestCase):
    """ Tests for importing quota tiers from YAML using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = default_server_base_dir

        # Create a temporary file for YAML content
        self.temp_file = NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize specialized importers
        self.quota_tier_importer = QuotaTierImporter(self.importer)
        self.security_importer = SecurityImporter(self.importer)

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

    def test_sync_quota_tiers(self):
        """ Tiers are created on the first sync and updated in place on the second one.
        """
        self._setup_test_environment()

        # Create a unique tier name for this test to avoid conflicts
        unique_suffix = uuid.uuid4().hex[:8]
        tier_defs = [self.yaml_config['quota_tier'][0].copy()]
        tier_defs[0]['name'] = f'enmasse.test_quota_tier_{unique_suffix}'

        # First sync - should create the tier
        created, updated = self.quota_tier_importer.sync_quota_tiers(tier_defs, self.session)

        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        tier_name = tier_defs[0]['name']
        self.assertIn(tier_name, self.quota_tier_importer.tier_defs)

        tier_id = self.quota_tier_importer.tier_defs[tier_name]['id']

        # Second sync - should update the tier in place, keeping its id stable
        created_2, updated_2 = self.quota_tier_importer.sync_quota_tiers(tier_defs, self.session)

        self.assertEqual(len(created_2), 0)
        self.assertEqual(len(updated_2), 1)

        tier_id_2 = self.quota_tier_importer.tier_defs[tier_name]['id']
        self.assertEqual(tier_id, tier_id_2)

# ################################################################################################################################

    def test_security_quota_tier_reference(self):
        """ A quota tier name on a security definition resolves to the tier's id.
        """
        self._setup_test_environment()

        # Create a unique tier for this test
        unique_suffix = uuid.uuid4().hex[:8]
        tier_defs = [self.yaml_config['quota_tier'][0].copy()]
        tier_defs[0]['name'] = f'enmasse.test_quota_tier_{unique_suffix}'

        _, _ = self.quota_tier_importer.sync_quota_tiers(tier_defs, self.session)

        # Make the orchestrating importer aware of the tiers just synced
        self.importer.quota_tier_defs = self.quota_tier_importer.tier_defs

        tier_name = tier_defs[0]['name']
        tier_id = self.quota_tier_importer.tier_defs[tier_name]['id']

        # Build a security definition referencing the tier by name
        sec_def = {
            'name': f'enmasse.test_quota_tier_sec_{unique_suffix}',
            'type': 'basic_auth',
            'username': f'enmasse.quota.{unique_suffix}',
            'password': 'abcdef123456',
            'quota_tier': tier_name,
        }

        created, _ = self.security_importer.sync_security_definitions([sec_def], self.session)

        self.assertEqual(len(created), 1)

        # The name must have been resolved to the tier's id
        self.assertEqual(sec_def['quota_tier'], tier_id)

# ################################################################################################################################

    def test_quota_tier_and_rate_limiting_are_mutually_exclusive(self):
        """ A security definition cannot reference a tier and carry its own rules at the same time.
        """
        self._setup_test_environment()

        unique_suffix = uuid.uuid4().hex[:8]

        sec_def = {
            'name': f'enmasse.test_quota_tier_excl_{unique_suffix}',
            'type': 'basic_auth',
            'username': f'enmasse.excl.{unique_suffix}',
            'password': 'abcdef123456',
            'quota_tier': 'enmasse.quota.tier.1',
            'rate_limiting': [{'cidr_list': ['0.0.0.0/0']}],
        }

        with self.assertRaises(ValueError):
            _ = self.security_importer.sync_security_definitions([sec_def], self.session)

# ################################################################################################################################

    def test_unknown_quota_tier_is_rejected(self):
        """ A reference to a tier that does not exist is an error.
        """
        self._setup_test_environment()

        unique_suffix = uuid.uuid4().hex[:8]

        sec_def = {
            'name': f'enmasse.test_quota_tier_missing_{unique_suffix}',
            'type': 'basic_auth',
            'username': f'enmasse.missing.{unique_suffix}',
            'password': 'abcdef123456',
            'quota_tier': f'enmasse.no.such.tier.{unique_suffix}',
        }

        with self.assertRaises(ValueError):
            _ = self.security_importer.sync_security_definitions([sec_def], self.session)

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
