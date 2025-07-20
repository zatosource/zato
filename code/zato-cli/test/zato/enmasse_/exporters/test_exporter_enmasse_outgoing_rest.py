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
import yaml

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.exporters.outgoing_rest import OutgoingRESTExporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import stranydict
    SASession = SASession
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingRESTExporter(TestCase):
    """ Tests exporting outgoing REST connections.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.security_importer = SecurityImporter(self.importer) # Security might be needed for outgoing connections
        self.outgoing_rest_importer = OutgoingRESTImporter(self.importer)

        # Exporter is needed to test the export functionality
        self.exporter = EnmasseYAMLExporter()
        self.outgoing_rest_exporter = OutgoingRESTExporter(self.exporter)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('SASession', None)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        # Ensure importer has cluster context
        _ = self.importer.get_cluster(self.session)

        # Import security definitions first, as outgoing connections may depend on them
        security_defs_from_yaml = self.yaml_config.get('security', [])
        if security_defs_from_yaml:
            # This method already populates self.importer.sec_defs after commit
            created_sec, updated_sec = self.security_importer.sync_security_definitions(security_defs_from_yaml, self.session)
            logger.info('Imported %d security definitions (created=%d, updated=%d)',
                len(created_sec) + len(updated_sec), len(created_sec), len(updated_sec))

            # Verify that security definitions were populated correctly
            logger.info('Security definitions in importer: %s', list(self.importer.sec_defs.keys()))

        _ = self.session.commit()

# ################################################################################################################################

    def test_outgoing_rest_export(self) -> 'None':
        """ Tests the export of outgoing REST connection definitions.
        """
        self._setup_test_environment()

        # Get outgoing REST connection definitions from the YAML template
        outgoing_rest_from_yaml = self.yaml_config.get('outgoing_rest', [])

        if outgoing_rest_from_yaml:
            logger.info('Found %d outgoing REST connections in test YAML template', len(outgoing_rest_from_yaml))

            # Import these definitions into the database to have something to export
            created, updated = self.outgoing_rest_importer.sync_outgoing_rest(outgoing_rest_from_yaml, self.session)
            _ = self.session.commit()

            # Verify that outgoing REST connections were imported
            self.assertTrue(len(created) + len(updated) > 0, 'No outgoing REST connections were created or updated from YAML.')

            # Test that the imported outgoing REST connections can be exported correctly
            all_exported_connections = self.outgoing_rest_exporter.export(self.session, self.importer.cluster_id)

            # Filter exported connections to only include those with names starting with "enmasse"
            exported_connections = [conn for conn in all_exported_connections if conn['name'].startswith('enmasse')]

            # Log the exported connections
            logger.info('Successfully exported %d outgoing REST connections (filtered to %d enmasse connections)',
                       len(all_exported_connections), len(exported_connections))

            # Verify the number of exported connections matches the number of imported connections
            self.assertEqual(len(exported_connections), len(created) + len(updated),
                f'Expected {len(created) + len(updated)} exported connections, got {len(exported_connections)}')

            # Extract expected connection data directly from the YAML template
            # Parse the template to get the expected values
            template_dict = yaml.safe_load(template_complex_01)

            # Build expected fields dictionary from the template
            required_conn_fields = {}
            for conn_def in template_dict.get('outgoing_rest', []):
                conn_name = conn_def['name']

                # Create a copy of the connection definition for expected fields
                conn_required = {
                    'name': conn_name,
                    'host': conn_def.get('host'),
                    'url_path': conn_def.get('url_path'),
                }

                # Add security if present
                if 'security' in conn_def and conn_def['security']:
                    conn_required['security'] = conn_def['security']

                # Add optional fields if present in the template
                for field in ['data_format', 'is_active', 'timeout', 'method', 'content_type', 'content_encoding', 'pool_size', 'ping_method', 'tls_verify']:
                    if field in conn_def and conn_def[field] is not None:
                        conn_required[field] = conn_def[field]

                # Add this connection's requirements to our dictionary
                required_conn_fields[conn_name] = conn_required

            # Verify each exported connection against required fields
            for conn in exported_connections:
                name = conn['name']
                self.assertIn(name, required_conn_fields, f'Unexpected connection {name} in export')
                expected = required_conn_fields[name]

                # Check all required fields in the connection definition
                # First check basic required fields that must always be present
                for field in ['name', 'host', 'url_path']:
                    self.assertIn(field, conn, f'Required field {field} missing in connection {name}')
                    self.assertEqual(conn[field], expected[field],
                        f'Field {field} has incorrect value in connection {name}, expected {expected[field]}, got {conn[field]}')

                # Then check optional fields that might be in expected but not always in exported data
                for field, value in expected.items():
                    if field not in ['name', 'host', 'url_path']:
                        if field in conn:
                            self.assertEqual(conn[field], value,
                                f'Field {field} has incorrect value in connection {name}, expected {value}, got {conn[field]}')
                        else:
                            logger.info(f'Optional field {field} not found in exported connection {name}, but was in template')
        else:
            logger.warning('No outgoing REST connections found in test YAML template')

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
