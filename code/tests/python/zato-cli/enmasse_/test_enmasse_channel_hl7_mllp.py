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

channel_hl7_mllp:

  - name: enmasse.hl7.mllp.1.{test_suffix}
    service: demo.ping
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

"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelHL7MLLPLive(BaseEnmasseTestCase):
    """ Live CLI tests for HL7 MLLP channel import, export, and reimport against a real server.
    """

    def _cleanup(self, test_suffix:'str') -> 'None':
        from zato.cli.enmasse.client import cleanup_enmasse
        cleanup_enmasse()

# ################################################################################################################################

    def test_hl7_mllp_import_export_reimport(self) -> 'None':
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
            _ = self.invoke_enmasse(export_path, is_import=False, is_export=True, include_type='channel_hl7_mllp')

            # .. read the exported file ..
            with open(export_path, 'r') as f:
                export_data = f.read()

            exported_dict = yaml.safe_load(export_data)

            # .. confirm the exported YAML has the channel_hl7_mllp key ..
            self.assertIn('channel_hl7_mllp', exported_dict, 'channel_hl7_mllp key missing from export')

            exported_channels = exported_dict['channel_hl7_mllp']

            # .. filter to our test channels ..
            test_channels = []
            for channel in exported_channels:
                if test_suffix in channel['name']:
                    test_channels.append(channel)

            test_channel_count = len(test_channels)
            self.assertEqual(test_channel_count, 3, f'Expected 3 HL7 MLLP channels, found {test_channel_count}')

            # .. verify key fields survived the round trip ..
            channels_by_name = {}
            for channel in test_channels:
                channels_by_name[channel['name']] = channel

            channel_1_name = f'enmasse.hl7.mllp.1.{test_suffix}'
            channel_2_name = f'enmasse.hl7.mllp.2.{test_suffix}'

            self.assertIn('service', channels_by_name[channel_1_name])
            self.assertEqual(channels_by_name[channel_1_name]['msh9_message_type'], 'ORU')

            self.assertEqual(channels_by_name[channel_2_name]['msh9_message_type'], 'ADT')
            self.assertEqual(channels_by_name[channel_2_name]['msh9_trigger_event'], 'A01')

            # .. now reimport the exported file to confirm idempotency ..
            _ = self.invoke_enmasse(export_path)

            # .. and export again to make sure nothing drifted.
            reimport_export_file_name = 'zato-enmasse-hl7-reimport-export-' + test_suffix + '.yaml'
            reimport_export_path = os.path.join(tmp_dir, reimport_export_file_name)

            _ = self.invoke_enmasse(reimport_export_path, is_import=False, is_export=True, include_type='channel_hl7_mllp')

            with open(reimport_export_path, 'r') as f:
                reimport_data = f.read()

            reimport_dict = yaml.safe_load(reimport_data)

            reimport_channels = []
            for channel in reimport_dict['channel_hl7_mllp']:
                if test_suffix in channel['name']:
                    reimport_channels.append(channel)

            reimport_count = len(reimport_channels)
            self.assertEqual(reimport_count, 3, f'Reimport produced {reimport_count} channels instead of 3')

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
