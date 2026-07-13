# -*- coding: utf-8 -*-
"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

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
from zato.cli.enmasse.exporters.as2 import AS2Exporter
from zato.cli.enmasse.importers.as2 import AS2Importer
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

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

class TestEnmasseOutgoingAS2Exporter(TestCase):
    """ Tests exporting outgoing AS2 connections.
    """

    def setUp(self) -> 'None':
        self.server_path = default_server_base_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.as2_importer = AS2Importer(self.importer)

        # Exporter is needed to test the export functionality
        self.exporter = EnmasseYAMLExporter()
        self.as2_exporter = AS2Exporter(self.exporter)

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

        # Clear existing data before importing
        cleanup_enmasse()
        _ = self.session.commit()

# ################################################################################################################################

    def test_outgoing_as2_export(self) -> 'None':
        """ Tests the export of outgoing AS2 connection definitions.
        """
        self._setup_test_environment()

        # Import the template's outgoing AS2 connections first
        outgoing_as2_list = self.yaml_config['outgoing_as2']
        created, updated = self.as2_importer.sync_definitions(outgoing_as2_list, self.session)
        _ = self.session.commit()

        logger.info('Imported %d outgoing AS2 connections (created=%d, updated=%d)',
            len(created) + len(updated), len(created), len(updated))

        # Export outgoing AS2 connections from the database
        cluster_id = self.importer.cluster_id
        exported_connections = self.as2_exporter.export(self.session, cluster_id)
        logger.info('Successfully exported %d outgoing AS2 connections', len(exported_connections))

        # The number of exported connections matches the number imported
        self.assertEqual(len(created) + len(updated), len(exported_connections))

        exported_by_name = {}
        for conn in exported_connections:
            exported_by_name[conn['name']] = conn

        # The fully specified connection round-trips with all its fields
        conn = exported_by_name['enmasse.outgoing.as2.1']

        self.assertEqual(conn['as2_from'], 'EnmasseRetail')
        self.assertEqual(conn['as2_to'], 'PartnerCorp')
        self.assertEqual(conn['endpoint_url'], 'https://as2.partnercorp.example.com/as2')
        self.assertEqual(conn['isa_qualifier'], 'ZZ')
        self.assertEqual(conn['isa_id'], 'PARTNERCORP')
        self.assertEqual(conn['gs_id'], 'PARTNERCORP')
        self.assertEqual(conn['sign_algorithm'], 'sha-256')
        self.assertEqual(conn['encryption_algorithm'], 'aes-128-cbc')
        self.assertEqual(conn['mdn_mode'], 'sync')
        self.assertEqual(conn['subject'], 'Enmasse AS2 message')
        self.assertEqual(conn['http_timeout_seconds'], 30)
        self.assertTrue(conn['compress'])

        # Toggles left at their defaults are not exported ..
        self.assertNotIn('sign', conn)
        self.assertNotIn('encrypt', conn)
        self.assertNotIn('verify_tls', conn)

        # .. an active connection does not say so explicitly ..
        self.assertNotIn('is_active', conn)

        # .. a connection with the audit log on does not export the flag ..
        self.assertNotIn('is_audit_log_active', conn)

        # .. and the private keys are never exported.
        self.assertNotIn('as2_signing_key', conn)
        self.assertNotIn('as2_decryption_key', conn)

# ################################################################################################################################

    def test_outgoing_as2_export_toggles_off(self) -> 'None':
        """ Tests that a connection with its security toggles off exports them explicitly.
        """
        self._setup_test_environment()

        outgoing_as2_list = self.yaml_config['outgoing_as2']
        _ = self.as2_importer.sync_definitions(outgoing_as2_list, self.session)
        _ = self.session.commit()

        cluster_id = self.importer.cluster_id
        exported_connections = self.as2_exporter.export(self.session, cluster_id)

        exported_by_name = {}
        for conn in exported_connections:
            exported_by_name[conn['name']] = conn

        conn = exported_by_name['enmasse.outgoing.as2.2']

        self.assertEqual(conn['as2_from'], 'EnmasseRetail')
        self.assertEqual(conn['as2_to'], 'LegacyPartner')
        self.assertEqual(conn['endpoint_url'], 'http://legacy.example.com:8080/as2')
        self.assertEqual(conn['mdn_mode'], 'none')
        self.assertEqual(conn['content_type'], 'application/edifact')
        self.assertEqual(conn['unb_id'], 'LEGACYPARTNER')

        # The toggles that differ from the defaults travel explicitly ..
        self.assertFalse(conn['sign'])
        self.assertFalse(conn['encrypt'])
        self.assertFalse(conn['verify_tls'])
        self.assertFalse(conn['is_audit_log_active'])

        # .. while the ones at their defaults stay out of the export ..
        self.assertNotIn('compress', conn)
        self.assertNotIn('mdn_signed', conn)

        # .. and fields the connection never had are absent too.
        self.assertNotIn('isa_qualifier', conn)
        self.assertNotIn('http_timeout_seconds', conn)

# ################################################################################################################################

    def test_outgoing_as2_export_to_dict(self) -> 'None':
        """ Tests that the full exporter includes the outgoing AS2 section.
        """
        self._setup_test_environment()

        outgoing_as2_list = self.yaml_config['outgoing_as2']
        created, _ = self.as2_importer.sync_definitions(outgoing_as2_list, self.session)
        _ = self.session.commit()

        exported_data = self.exporter.export_to_dict(self.session)

        self.assertIn('outgoing_as2', exported_data, 'Exporter did not produce an "outgoing_as2" section.')
        self.assertEqual(len(exported_data['outgoing_as2']), len(created))

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
