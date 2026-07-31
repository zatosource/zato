# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.exporters.outgoing_fhir import OutgoingFHIRExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.outgoing_fhir import OutgoingFHIRImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.defaults import default_server_base_dir
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

template_outgoing_fhir = """

security:

  - name: enmasse.fhir.export.basic_auth.1
    type: basic_auth
    username: enmasse.fhir.export.1
    password: Zato_Enmasse_Env.FHIRExportBasicAuth1

outgoing_fhir:

  - name: enmasse.fhir.export.1
    address: http://127.0.0.1:31101/fhir/r4
    pool_size: 7
    security: enmasse.fhir.export.basic_auth.1
    is_audit_log_active: true

  - name: enmasse.fhir.export.2
    address: http://127.0.0.1:31102/fhir/r4

"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingFHIRExporter(TestCase):
    """ Tests exporting outgoing HL7 FHIR connections.
    """

    def setUp(self) -> 'None':

        self.server_path = default_server_base_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_outgoing_fhir.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.outgoing_fhir_importer = OutgoingFHIRImporter(self.importer)

        # A connection may name a security definition, so the definitions have to exist first
        self.security_importer = SecurityImporter(self.importer)

        # Exporter under test
        self.exporter = EnmasseYAMLExporter()
        self.outgoing_fhir_exporter = OutgoingFHIRExporter(self.exporter)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('SASession', None)

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

        # A connection that names a security definition can only resolve it once the definitions exist,
        # which is the order the importer itself runs the two sections in
        security_list = self.yaml_config['security']
        _ = self.security_importer.sync_security_definitions(security_list, self.session)

# ################################################################################################################################

    def _import_and_export(self) -> 'stranydict':
        """ Imports what the file declares and answers with the export, keyed by connection name.
        """
        self._setup_test_environment()

        connection_defs = self.yaml_config['outgoing_fhir']
        _, _ = self.outgoing_fhir_importer.sync_definitions(connection_defs, self.session)

        all_exported = self.outgoing_fhir_exporter.export(self.session, self.importer.cluster_id)

        out = {}

        for item in all_exported:
            if item['name'].startswith('enmasse.fhir.export.'):
                out[item['name']] = item

        return out

# ################################################################################################################################

    def test_only_what_a_connection_was_configured_away_from_is_written(self) -> 'None':
        """ A field left at its default is not written out, so a file this export produces reads
        the way one written by hand does.
        """
        exported_by_name = self._import_and_export()

        exported_count = len(exported_by_name)
        self.assertEqual(exported_count, 2)

        # The first connection moved three fields away from their defaults ..
        item = exported_by_name['enmasse.fhir.export.1']
        self.assertEqual(item['address'], 'http://127.0.0.1:31101/fhir/r4')
        self.assertEqual(item['pool_size'], 7)
        self.assertTrue(item['is_audit_log_active'])

        # .. and left this one where it was, so it is not written out ..
        self.assertNotIn('is_active', item)

        # .. while the second one moved nothing at all.
        item = exported_by_name['enmasse.fhir.export.2']
        self.assertEqual(item['address'], 'http://127.0.0.1:31102/fhir/r4')
        self.assertNotIn('pool_size', item)
        self.assertNotIn('is_audit_log_active', item)

# ################################################################################################################################

    def test_the_security_definition_comes_back_by_name(self) -> 'None':
        """ What is stored is the definition's id, which means nothing in another environment,
        so the export carries the name it goes by instead.
        """
        exported_by_name = self._import_and_export()

        item = exported_by_name['enmasse.fhir.export.1']
        self.assertEqual(item['security'], 'enmasse.fhir.export.basic_auth.1')
        self.assertNotIn('security_id', item)

        # A connection with no definition of its own carries neither
        item = exported_by_name['enmasse.fhir.export.2']
        self.assertNotIn('security', item)
        self.assertNotIn('security_id', item)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
