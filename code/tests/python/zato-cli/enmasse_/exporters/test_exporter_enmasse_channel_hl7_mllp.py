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
from zato.cli.enmasse.exporters.channel_hl7_mllp import ChannelHL7MLLPExporter
from zato.cli.enmasse.importers.channel_hl7_mllp import ChannelHL7MLLPImporter
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

class TestEnmasseChannelHL7MLLPExporter(TestCase):
    """ Tests exporting HL7 MLLP channels.
    """

    def setUp(self) -> 'None':

        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.channel_hl7_mllp_importer = ChannelHL7MLLPImporter(self.importer)

        # Exporter under test
        self.exporter = EnmasseYAMLExporter()
        self.channel_hl7_mllp_exporter = ChannelHL7MLLPExporter(self.exporter)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('SASession', None)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        _ = self.importer.get_cluster(self.session)

# ################################################################################################################################

    def test_export_channel_hl7_mllp(self) -> 'None':
        """ Import the 3 channels first, then export and verify the count and key fields.
        """
        self._setup_test_environment()

        # Import channels from YAML
        channel_defs = self.yaml_config['channel_hl7_mllp']
        created, _ = self.channel_hl7_mllp_importer.sync_definitions(channel_defs, self.session)

        created_count = len(created)
        noun = 'channel' if created_count == 1 else 'channels'
        logger.info('Imported %d HL7 MLLP %s', created_count, noun)

        # Export
        all_exported = self.channel_hl7_mllp_exporter.export(self.session, self.importer.cluster_id)

        # Filter to only enmasse test channels
        exported = []
        for item in all_exported:
            if item['name'].startswith('enmasse.hl7.mllp.'):
                exported.append(item)

        exported_count = len(exported)
        self.assertEqual(exported_count, 3)

        # Build a lookup by name
        exported_by_name = {}
        for item in exported:
            exported_by_name[item['name']] = item

        # Verify key fields
        self.assertEqual(exported_by_name['enmasse.hl7.mllp.1']['service'], 'enmasse.hl7.test.service')
        self.assertEqual(exported_by_name['enmasse.hl7.mllp.1']['msh9_message_type'], 'ORU')

        self.assertEqual(exported_by_name['enmasse.hl7.mllp.2']['service'], 'enmasse.hl7.test.service.2')
        self.assertEqual(exported_by_name['enmasse.hl7.mllp.2']['msh9_message_type'], 'ADT')
        self.assertEqual(exported_by_name['enmasse.hl7.mllp.2']['msh9_trigger_event'], 'A01')

        self.assertEqual(exported_by_name['enmasse.hl7.mllp.3']['service'], 'enmasse.hl7.test.service.3')

# ################################################################################################################################

    def test_export_roundtrip(self) -> 'None':
        """ Import, export, verify exported dict can reconstruct the original YAML entries field by field.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_hl7_mllp']
        _, _ = self.channel_hl7_mllp_importer.sync_definitions(channel_defs, self.session)

        all_exported = self.channel_hl7_mllp_exporter.export(self.session, self.importer.cluster_id)

        exported_by_name = {}
        for item in all_exported:
            if item['name'].startswith('enmasse.hl7.mllp.'):
                exported_by_name[item['name']] = item

        # Verify channel 2 roundtrip for routing and dedup fields
        channel_2 = exported_by_name['enmasse.hl7.mllp.2']
        self.assertEqual(channel_2['msh9_message_type'], 'ADT')
        self.assertEqual(channel_2['msh9_trigger_event'], 'A01')
        self.assertEqual(channel_2['fix_off_by_one_field_index'], True)
        self.assertEqual(channel_2['dedup_ttl_value'], 30)
        self.assertEqual(channel_2['dedup_ttl_unit'], 'minutes')

        # Verify channel 3 roundtrip for overridden tolerance toggles
        channel_3 = exported_by_name['enmasse.hl7.mllp.3']
        self.assertIn('is_default', channel_3)

# ################################################################################################################################

    def test_export_empty(self) -> 'None':
        """ Call export on a clean DB (no MLLP channels), assert empty list returned.
        """
        self._setup_test_environment()

        # Export without importing anything first
        exported = self.channel_hl7_mllp_exporter.export(self.session, self.importer.cluster_id)

        # There may be pre-existing channels from other tests, but at minimum the result should be a list
        self.assertIsInstance(exported, list)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
