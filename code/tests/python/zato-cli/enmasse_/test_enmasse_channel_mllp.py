# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import basicConfig, getLogger, WARN
from tempfile import gettempdir
from unittest import main

# PyYAML
import yaml

# Zato
from zato.common.test import rand_string, rand_unicode
from zato.common.test.enmasse_.base import BaseEnmasseTestCase
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Channel_HL7_MLLP_Template = """

security:

  - name: enmasse.hl7.mllp.mtls.{test_suffix}
    type: mtls
    client_cert_subject_dn: CN=enmasse.hl7.client,O=Enmasse,C=US

channel_mllp:

  - name: enmasse.hl7.mllp.1.{test_suffix}
    service: demo.ping
    security: enmasse.hl7.mllp.mtls.{test_suffix}
    should_validate: true
    msh9_message_type: ORU

  - name: enmasse.hl7.mllp.2.{test_suffix}
    service: demo.ping
    msh9_message_type: ADT
    msh9_trigger_event: A01
    fix_off_by_one_field_index: true
    dedup_ttl_value: 30
    dedup_ttl_unit: minutes

  - name: enmasse.hl7.mllp.3.{test_suffix}
    service: demo.ping
    is_default: true
    normalize_obx2_value_type: false
    allow_short_encoding_characters: false
    destinations:
      - name: enmasse.hl7.dest.rest.{test_suffix}
        type: rest
        connection: enmasse.hl7.dest.rest.{test_suffix}
        is_active: true
        options:
          method: POST
      - name: enmasse.hl7.dest.forward.{test_suffix}
        type: hl7-mllp
        connection: enmasse.hl7.dest.forward.{test_suffix}
        is_active: false
    respond_from: enmasse.hl7.dest.rest.{test_suffix}
    delivery_mode: in-order

  - name: enmasse.hl7.mllp.4.{test_suffix}
    destinations:
      - name: enmasse.hl7.dest.forward.{test_suffix}
        type: hl7-mllp
        connection: enmasse.hl7.dest.forward.{test_suffix}

"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelMLLPLive(BaseEnmasseTestCase):
    """ Live CLI tests for HL7 MLLP channel import, export, and reimport against a real server.
    """

    def _cleanup(self, test_suffix:'str') -> 'None':
        from zato.cli.enmasse.client import cleanup_enmasse
        from zato.common.defaults import default_server_base_dir
        cleanup_enmasse(default_server_base_dir)

# ################################################################################################################################

    def test_mllp_import_export_reimport(self) -> 'None':
        """ Full cycle: import HL7 MLLP channels, export them, verify the export, then reimport to confirm idempotency.
        """

        # sh
        from sh import ErrorReturnCode

        os.environ['Zato_Needs_Config_Reload'] = 'False'

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        import_file_name = 'zato-enmasse-hl7-import-' + test_suffix + '.yaml'
        export_file_name = 'zato-enmasse-hl7-export-' + test_suffix + '.yaml'

        import_path = os.path.join(tmp_dir, import_file_name)
        export_path = os.path.join(tmp_dir, export_file_name)

        # Prepare the import file from the template ..
        data = _Channel_HL7_MLLP_Template.format(test_suffix=test_suffix)

        with open_w(import_path) as f:
            _ = f.write(data)

        try:

            # .. import the HL7 MLLP channels ..
            _ = self.invoke_enmasse(import_path)

            # .. export them back out ..
            _ = self.invoke_enmasse(
                export_path, is_import=False, is_export=True, include_type='channel_mllp,security')

            # .. read the exported file ..
            with open(export_path, 'r') as f:
                export_data = f.read()

            exported_dict = yaml.safe_load(export_data)

            # .. confirm the exported YAML has the channel_mllp key ..
            self.assertIn('channel_mllp', exported_dict, 'channel_mllp key missing from export')

            exported_channels = exported_dict['channel_mllp']

            # .. filter to our test channels ..
            test_channels = []
            for channel in exported_channels:
                if test_suffix in channel['name']:
                    test_channels.append(channel)

            test_channel_count = len(test_channels)
            self.assertEqual(test_channel_count, 4, f'Expected 4 HL7 MLLP channels, found {test_channel_count}')

            # .. verify key fields survived the round trip ..
            channels_by_name = {}
            for channel in test_channels:
                channels_by_name[channel['name']] = channel

            channel_1_name = f'enmasse.hl7.mllp.1.{test_suffix}'
            channel_2_name = f'enmasse.hl7.mllp.2.{test_suffix}'
            channel_3_name = f'enmasse.hl7.mllp.3.{test_suffix}'
            channel_4_name = f'enmasse.hl7.mllp.4.{test_suffix}'

            self.assertIn('service', channels_by_name[channel_1_name])
            self.assertEqual(channels_by_name[channel_1_name]['msh9_message_type'], 'ORU')

            self.assertEqual(channels_by_name[channel_2_name]['msh9_message_type'], 'ADT')
            self.assertEqual(channels_by_name[channel_2_name]['msh9_trigger_event'], 'A01')

            # .. the security definition the first channel names travels by name in both directions,
            # .. the id it resolved to never appearing in the export ..
            channel_1 = channels_by_name[channel_1_name]
            self.assertEqual(channel_1['security'], f'enmasse.hl7.mllp.mtls.{test_suffix}')
            self.assertNotIn('security_id', channel_1)

            # .. while a channel that names none carries neither key ..
            channel_2 = channels_by_name[channel_2_name]
            self.assertNotIn('security', channel_2)
            self.assertNotIn('security_id', channel_2)

            # .. a channel's destinations come back as a list rather than as the text they are
            # .. stored as, each one keeping the options and the switch it went in with ..
            channel_3 = channels_by_name[channel_3_name]
            destinations = channel_3['destinations']

            self.assertEqual(len(destinations), 2)

            self.assertEqual(destinations[0]['connection'], f'enmasse.hl7.dest.rest.{test_suffix}')
            self.assertEqual(destinations[0]['type'], 'rest')
            self.assertTrue(destinations[0]['is_active'])
            self.assertEqual(destinations[0]['options']['method'], 'POST')

            self.assertEqual(destinations[1]['type'], 'hl7-mllp')
            self.assertFalse(destinations[1]['is_active'])

            # .. a destination with no options of its own carries no options key at all ..
            self.assertNotIn('options', destinations[1])

            # .. and the reply and the order the rest are delivered in travel too ..
            self.assertEqual(channel_3['respond_from'], f'enmasse.hl7.dest.rest.{test_suffix}')
            self.assertEqual(channel_3['delivery_mode'], 'in-order')

            # .. a channel that delivers to its destinations alone needs no service, and the two
            # .. defaults it never set stay out of the export ..
            channel_4 = channels_by_name[channel_4_name]

            self.assertNotIn('service', channel_4)
            self.assertNotIn('respond_from', channel_4)
            self.assertNotIn('delivery_mode', channel_4)
            self.assertEqual(len(channel_4['destinations']), 1)

            # .. now reimport the exported file to confirm idempotency ..
            _ = self.invoke_enmasse(export_path)

            # .. and export again to make sure nothing drifted.
            reimport_export_file_name = 'zato-enmasse-hl7-reimport-export-' + test_suffix + '.yaml'
            reimport_export_path = os.path.join(tmp_dir, reimport_export_file_name)

            _ = self.invoke_enmasse(reimport_export_path, is_import=False, is_export=True, include_type='channel_mllp')

            with open(reimport_export_path, 'r') as f:
                reimport_data = f.read()

            reimport_dict = yaml.safe_load(reimport_data)

            reimport_channels = []
            for channel in reimport_dict['channel_mllp']:
                if test_suffix in channel['name']:
                    reimport_channels.append(channel)

            reimport_count = len(reimport_channels)
            self.assertEqual(reimport_count, 4, f'Reimport produced {reimport_count} channels instead of 4')

            # The destination list survives being imported from an export as it does from a
            # hand-written file, which is what makes one environment's export the next one's input.
            for channel in reimport_channels:
                if channel['name'] == channel_3_name:
                    self.assertEqual(len(channel['destinations']), 2)
                    self.assertEqual(channel['respond_from'], f'enmasse.hl7.dest.rest.{test_suffix}')
                    break
            else:
                self.fail(f'Channel `{channel_3_name}` was not exported after the reimport')

            if os.path.exists(reimport_export_path):
                os.remove(reimport_export_path)

        except ErrorReturnCode as error:
            stdout = error.stdout.decode('utf8')
            stderr = error.stderr

            self._warn_on_error(stdout, stderr)
            self.fail(f'Caught an exception during HL7 MLLP import-export-reimport; stdout -> {stdout}')

        finally:
            if os.path.exists(import_path):
                os.remove(import_path)
            if os.path.exists(export_path):
                os.remove(export_path)

            self._cleanup(test_suffix)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
