# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.email_smtp import SMTPImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseEmailSMTPExporter(TestCase):
    """ Tests exporting email SMTP connection definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.smtp_importer = SMTPImporter(self.importer)

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
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_email_smtp_export(self):
        self._setup_test_environment()

        # 1. Get email SMTP connection definitions from the YAML template
        smtp_list_from_yaml = self.yaml_config.get('email_smtp', [])

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_smtp, _ = self.smtp_importer.sync_smtp_definitions(smtp_list_from_yaml, self.session)
        self.session.commit()

        self.assertTrue(len(created_smtp) > 0, 'No email SMTP connection definitions were created from YAML.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('email_smtp', exported_data, 'Exporter did not produce an "email_smtp" section.')
        exported_smtp_list = exported_data['email_smtp']

        # 4. Compare exported data with the original YAML data
        self.assertEqual(len(exported_smtp_list), len(smtp_list_from_yaml), 'Number of exported SMTP connections does not match original YAML.')

        # Create dictionaries keyed by name for easier comparison
        yaml_smtp_by_name = {item['name']: item for item in smtp_list_from_yaml}
        exported_smtp_by_name = {item['name']: item for item in exported_smtp_list}

        for name, yaml_def in yaml_smtp_by_name.items():
            self.assertIn(name, exported_smtp_by_name, f'SMTP connection "{name}" from YAML not found in export.')
            exported_def = exported_smtp_by_name[name]

            # Check common fields that should be exported - excluding password
            self.assertEqual(exported_def.get('name'), yaml_def.get('name'), f'Name mismatch for SMTP connection "{name}"')
            self.assertEqual(exported_def.get('host'), yaml_def.get('host'), f'Host mismatch for SMTP connection "{name}"')

            # Check username if provided
            if 'username' in yaml_def and yaml_def['username']:
                self.assertEqual(exported_def.get('username'), yaml_def.get('username'), f'Username mismatch for SMTP connection "{name}"')

            # Check optional fields if present in YAML
            for field in ['port', 'timeout', 'ping_address', 'is_tls', 'debug_level', 'mode', 'is_active']:
                if field in yaml_def and yaml_def[field] is not None:
                    self.assertEqual(exported_def.get(field), yaml_def.get(field), f'Field {field} mismatch for SMTP connection "{name}"')

            # Verify password is not exported
            self.assertNotIn('password', exported_def, f'Password was exported for SMTP connection "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
