# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from unittest import TestCase, main
import uuid

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.audit_extraction import AuditExtractionImporter
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseAuditExtraction(TestCase):
    """ Tests for importing attribute-extraction rule sets from YAML using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()
        self.audit_extraction_importer = AuditExtractionImporter(self.importer)

        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

# ################################################################################################################################

    def test_sync_extraction_rules(self) -> 'None':
        """ Rule sets are created on the first sync and updated in place on the second one.
        """
        self._setup_test_environment()

        # Create a unique set name for this test to avoid conflicts
        unique_suffix = uuid.uuid4().hex[:8]

        extraction_defs = [{
            'name': f'enmasse.test_audit_extraction_{unique_suffix}',
            'source': 'rest-channel',
            'rules': [
                {'attr_name': 'customer_id', 'rule_type': 'json-path', 'expression': '$.request.customer_id'},
                {'attr_name': 'order_id', 'rule_type': 'header', 'expression': 'X-Order-ID'},
            ],
        }]

        # First sync - should create the set
        created, updated = self.audit_extraction_importer.sync_extraction_rules(extraction_defs, self.session)

        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        extraction_name = extraction_defs[0]['name']
        self.assertIn(extraction_name, self.audit_extraction_importer.extraction_defs)

        extraction_id = self.audit_extraction_importer.extraction_defs[extraction_name]['id']

        # Second sync - should update the set in place, keeping its id stable
        created_2, updated_2 = self.audit_extraction_importer.sync_extraction_rules(extraction_defs, self.session)

        self.assertEqual(len(created_2), 0)
        self.assertEqual(len(updated_2), 1)

        extraction_id_2 = self.audit_extraction_importer.extraction_defs[extraction_name]['id']
        self.assertEqual(extraction_id, extraction_id_2)

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
