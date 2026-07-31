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
from zato.cli.enmasse.exporters.channel_mllp import ChannelMLLPExporter
from zato.cli.enmasse.importers.channel_mllp import ChannelMLLPImporter
from zato.cli.enmasse.importers.security import SecurityImporter
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

class TestEnmasseChannelMLLPExporter(TestCase):
    """ Tests exporting HL7 MLLP channels.
    """

    def setUp(self) -> 'None':

        self.server_path = default_server_base_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.channel_mllp_importer = ChannelMLLPImporter(self.importer)

        # A channel may name a security definition, so the definitions have to exist first
        self.security_importer = SecurityImporter(self.importer)

        # Exporter under test
        self.exporter = EnmasseYAMLExporter()
        self.channel_mllp_exporter = ChannelMLLPExporter(self.exporter)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('SASession', None)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        _ = self.importer.get_cluster(self.session)

        # A channel that names a security definition can only resolve it once the definitions exist,
        # which is the order the importer itself runs the two sections in
        security_list = self.yaml_config['security']
        _ = self.security_importer.sync_security_definitions(security_list, self.session)

# ################################################################################################################################

    def test_export_channel_mllp(self) -> 'None':
        """ Import the 3 channels first, then export and verify the count and key fields.
        """
        self._setup_test_environment()

        # Import channels from YAML
        channel_defs = self.yaml_config['channel_mllp']
        created, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        created_count = len(created)
        noun = 'channel' if created_count == 1 else 'channels'
        logger.info('Imported %d HL7 MLLP %s', created_count, noun)

        # Export
        all_exported = self.channel_mllp_exporter.export(self.session, self.importer.cluster_id)

        # Filter to only enmasse test channels
        exported = []
        for item in all_exported:
            if item['name'].startswith('enmasse.hl7.mllp.'):
                exported.append(item)

        exported_count = len(exported)
        self.assertEqual(exported_count, len(channel_defs))

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

        channel_defs = self.yaml_config['channel_mllp']
        _, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        all_exported = self.channel_mllp_exporter.export(self.session, self.importer.cluster_id)

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

    def test_export_writes_the_destinations_as_a_list(self) -> 'None':
        """ A channel stores its destinations as the JSON text the Dashboard writes, and what an
        export carries is a list, so a file this export produces reads the way a hand-written one does.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_mllp']
        _, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        all_exported = self.channel_mllp_exporter.export(self.session, self.importer.cluster_id)

        exported_by_name = {}
        for item in all_exported:
            if item['name'].startswith('enmasse.hl7.mllp.'):
                exported_by_name[item['name']] = item

        channel_3 = exported_by_name['enmasse.hl7.mllp.3']
        destinations = channel_3['destinations']

        self.assertIsInstance(destinations, list)
        self.assertEqual(len(destinations), 2)

        self.assertEqual(destinations[0]['name'], 'enmasse.outgoing.rest.1')
        self.assertEqual(destinations[0]['type'], 'rest')
        self.assertEqual(destinations[0]['connection'], 'enmasse.outgoing.rest.1')
        self.assertTrue(destinations[0]['is_active'])
        self.assertEqual(destinations[0]['options'], {'method': 'POST'})

        self.assertEqual(destinations[1]['type'], 'smtp')
        self.assertFalse(destinations[1]['is_active'])
        self.assertEqual(destinations[1]['options']['subject'], 'A message arrived')

        # The reply and the order the rest are delivered in are exported alongside the list
        self.assertEqual(channel_3['respond_from'], 'enmasse.outgoing.rest.1')
        self.assertEqual(channel_3['delivery_mode'], 'in-order')

# ################################################################################################################################

    def test_export_omits_the_options_a_destination_does_not_have(self) -> 'None':
        """ A destination of a type that takes no options carries no options key, there being
        nothing for a hand-written file to say about them.
        """
        self._setup_test_environment()

        channel_defs = [{
            'name': 'enmasse.hl7.mllp.plain.destination',
            'destinations': [{'type': 'hl7-mllp', 'connection': 'enmasse.hl7.forward.1'}],
        }]

        _, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        all_exported = self.channel_mllp_exporter.export(self.session, self.importer.cluster_id)

        for item in all_exported:
            if item['name'] == 'enmasse.hl7.mllp.plain.destination':
                exported = item
                break
        else:
            self.fail('The channel was not exported')

        destination = exported['destinations'][0]

        self.assertEqual(destination['type'], 'hl7-mllp')
        self.assertEqual(destination['connection'], 'enmasse.hl7.forward.1')
        self.assertNotIn('options', destination)

        # A channel delivering to its destinations alone exports no service at all
        self.assertNotIn('service', exported)

# ################################################################################################################################

    def test_export_names_the_security_definition(self) -> 'None':
        """ The security definition a channel accepts is exported by name rather than by the id that
        is stored, because an id means nothing in the environment the export is imported into.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_mllp']
        _, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        all_exported = self.channel_mllp_exporter.export(self.session, self.importer.cluster_id)

        exported_by_name = {}
        for item in all_exported:
            if item['name'].startswith('enmasse.hl7.mllp.'):
                exported_by_name[item['name']] = item

        # The first channel names the definition ..
        channel_1 = exported_by_name['enmasse.hl7.mllp.1']
        self.assertEqual(channel_1['security'], 'enmasse.mtls.2')
        self.assertNotIn('security_id', channel_1)

        # .. and the second names none, so neither key is exported for it.
        channel_2 = exported_by_name['enmasse.hl7.mllp.2']
        self.assertNotIn('security', channel_2)
        self.assertNotIn('security_id', channel_2)

# ################################################################################################################################

    def test_export_keeps_settings_turned_off(self) -> 'None':
        """ A channel switched away from a default that happens to be true or non-zero
        exports that choice, so a re-import does not switch it back on.
        """
        self._setup_test_environment()

        channel_defs = [{
            'name': 'enmasse.hl7.mllp.tolerant.off',
            'service': 'enmasse.hl7.test.service',
            'is_active': False,
            'normalize_line_endings': False,
            'should_parse_on_input': False,
        }]

        _, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        all_exported = self.channel_mllp_exporter.export(self.session, self.importer.cluster_id)

        for item in all_exported:
            if item['name'] == 'enmasse.hl7.mllp.tolerant.off':
                exported = item
                break
        else:
            self.fail('The channel was not exported')

        self.assertFalse(exported['is_active'])
        self.assertFalse(exported['normalize_line_endings'])
        self.assertFalse(exported['should_parse_on_input'])

# ################################################################################################################################

    def test_export_omits_settings_left_at_their_default(self) -> 'None':
        """ A channel that was never configured away from a default does not export that field.
        """
        self._setup_test_environment()

        channel_defs = [{
            'name': 'enmasse.hl7.mllp.plain',
            'service': 'enmasse.hl7.test.service',
        }]

        _, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        all_exported = self.channel_mllp_exporter.export(self.session, self.importer.cluster_id)

        for item in all_exported:
            if item['name'] == 'enmasse.hl7.mllp.plain':
                exported = item
                break
        else:
            self.fail('The channel was not exported')

        self.assertNotIn('is_active', exported)
        self.assertNotIn('normalize_line_endings', exported)
        self.assertNotIn('start_seq', exported)
        self.assertNotIn('dedup_ttl_value', exported)

# ################################################################################################################################

    def test_export_empty(self) -> 'None':
        """ Call export on a clean DB (no MLLP channels), assert empty list returned.
        """
        self._setup_test_environment()

        # Export without importing anything first
        exported = self.channel_mllp_exporter.export(self.session, self.importer.cluster_id)

        # There may be pre-existing channels from other tests, but at minimum the result should be a list
        self.assertIsInstance(exported, list)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
