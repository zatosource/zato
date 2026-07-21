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
from zato.cli.enmasse.exporters.outgoing_as4 import OutgoingAS4Exporter
from zato.cli.enmasse.importers.outgoing_as4 import OutgoingAS4Importer
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

class TestEnmasseOutgoingAS4Exporter(TestCase):
    """ Tests exporting outgoing AS4 connections.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.outgoing_as4_importer = OutgoingAS4Importer(self.importer)

        # Exporter is needed to test the export functionality
        self.exporter = EnmasseYAMLExporter()
        self.outgoing_as4_exporter = OutgoingAS4Exporter(self.exporter)

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
        cleanup_enmasse(self.server_path)
        _ = self.session.commit()

# ################################################################################################################################

    def test_outgoing_as4_export(self) -> 'None':
        """ Tests the export of outgoing AS4 connection definitions.
        """
        self._setup_test_environment()

        # Import the template's outgoing AS4 connections first
        outgoing_as4_list = self.yaml_config['outgoing_as4']
        created, updated = self.outgoing_as4_importer.sync_outgoing_as4(outgoing_as4_list, self.session)
        _ = self.session.commit()

        logger.info('Imported %d outgoing AS4 connections (created=%d, updated=%d)',
            len(created) + len(updated), len(created), len(updated))

        # Export outgoing AS4 connections from the database
        cluster_id = self.importer.cluster_id
        exported_connections = self.outgoing_as4_exporter.export(self.session, cluster_id)
        logger.info('Successfully exported %d outgoing AS4 connections', len(exported_connections))

        # The number of exported connections matches the number imported
        self.assertEqual(len(created) + len(updated), len(exported_connections))

        exported_by_name = {}
        for conn in exported_connections:
            exported_by_name[conn['name']] = conn

        # The discovery-driven Peppol connection round-trips with all its fields
        conn = exported_by_name['enmasse.outgoing.as4.1']

        self.assertEqual(conn['host'], 'https://ap.example.com')
        self.assertEqual(conn['url_path'], '/as4')
        self.assertEqual(conn['timeout'], 20)
        self.assertEqual(conn['as4_profile'], 'peppol')
        self.assertEqual(conn['as4_from_party'], 'enmasse-ap')
        self.assertEqual(conn['as4_original_sender'], '0192:991825827')
        self.assertTrue(conn['as4_use_discovery'])
        self.assertEqual(conn['as4_sml_domain'], 'acc.edelivery.tech.ec.europa.eu')

        # Validated TLS is the default, so it is not exported
        self.assertNotIn('validate_tls', conn)

# ################################################################################################################################

    def test_outgoing_as4_export_opaque_fields(self) -> 'None':
        """ Tests that the AS4 fields round-trip through the exporter.
        """
        self._setup_test_environment()

        outgoing_as4_list = self.yaml_config['outgoing_as4']
        _ = self.outgoing_as4_importer.sync_outgoing_as4(outgoing_as4_list, self.session)
        _ = self.session.commit()

        cluster_id = self.importer.cluster_id
        exported_connections = self.outgoing_as4_exporter.export(self.session, cluster_id)

        exported_by_name = {}
        for conn in exported_connections:
            exported_by_name[conn['name']] = conn

        conn = exported_by_name['enmasse.outgoing.as4.2']

        self.assertFalse(conn['validate_tls'])
        self.assertEqual(conn['as4_profile'], 'ics2')
        self.assertEqual(conn['as4_from_party'], 'enmasse-eori')
        self.assertEqual(conn['as4_to_party'], 'sti-taxud')
        self.assertEqual(conn['as4_service'], 'eu.customs.ics2')
        self.assertEqual(conn['as4_action'], 'IE3F26')
        self.assertEqual(conn['as4_mpc'], 'urn:fdc:ec.europa.eu:2019:mpc')

        # Fields the connection never had are absent from its export
        self.assertNotIn('as4_use_discovery', conn)
        self.assertNotIn('as4_sml_domain', conn)
        self.assertNotIn('as4_signing_key', conn)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
