# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main
import uuid

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.audit_extraction import AuditExtractionImporter
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseAuditExtractionExporter(TestCase):
    """ Tests exporting attribute-extraction rule sets to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = default_server_base_dir

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.audit_extraction_importer = AuditExtractionImporter(self.importer)

        self.session = cast_('any_', None)

        # The rule set this test creates and expects to see exported back
        unique_suffix = uuid.uuid4().hex[:8]

        self.extraction_def = {
            'name': f'enmasse.test_audit_extraction_export_{unique_suffix}',
            'source': 'hl7',
            'rules': [
                {'attr_name': 'mrn', 'rule_type': 'regex', 'expression': r'PID\|.*?\|(?P<value>[^|^]+)'},
                {'attr_name': 'sending_facility', 'rule_type': 'regex', 'expression': r'MSH\|[^|]*\|[^|]*\|(?P<value>[^|]+)'},
            ],
        }

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        # Ensure importer has cluster context
        _ = self.importer.get_cluster(self.session)

        # Import the extraction rule set definition
        _, _ = self.audit_extraction_importer.sync_extraction_rules([self.extraction_def], self.session)

        self.session.commit()

# ################################################################################################################################

    def test_audit_extraction_export(self) -> 'None':
        """ Tests the export of extraction rule set definitions - a full round-trip.
        """
        self._setup_test_environment()

        # Initialize the exporter
        yaml_exporter = EnmasseYAMLExporter()

        # Export the data
        exported_data = yaml_exporter.export_to_dict(self.session)

        # Get the extraction rule set section
        exported_extraction = exported_data.get('audit_extraction', [])

        # Take into account only the set this test created
        exported_extraction_dict = {item['name']: item for item in exported_extraction}

        extraction_name = self.extraction_def['name']
        self.assertIn(extraction_name, exported_extraction_dict, f'Exported sets missing set: {extraction_name}')

        exported_set = exported_extraction_dict[extraction_name]

        # Every field must round-trip unchanged, the rules in their original order
        self.assertEqual(exported_set['source'], self.extraction_def['source'])
        self.assertEqual(exported_set['rules'], self.extraction_def['rules'])

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        cleanup_enmasse()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
