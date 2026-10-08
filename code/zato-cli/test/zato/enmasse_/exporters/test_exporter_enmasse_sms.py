# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from unittest import TestCase

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.exporters.sms import Env_Reference_Prefix
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.sms import Channel_Outconn_Key, ChannelSMSImporter, OutgoingSMSImporter
from zato.common.api import SMS
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

_scheduler = SMS.Scheduler

_outgoing_twilio = 'enmasse.sms.outgoing.twilio'
_outgoing_vonage = 'enmasse.sms.outgoing.vonage'
_channel_polling = 'enmasse.sms.channel.polling'
_channel_webhook = 'enmasse.sms.channel.webhook'

template_sms = f"""
outgoing_sms:
  - name: {_outgoing_twilio}
    provider: twilio
    username: ACenmasse
    password: enmasse.twilio.auth.token
    sender: '+12025550100'
    pool_size: 5

  - name: {_outgoing_vonage}
    is_active: false
    provider: vonage
    username: enmasse-vonage-key
    password: enmasse.vonage.api.secret
    signature_secret: enmasse.vonage.signature.secret
    sender: '+12025550101'

channel_sms:
  - name: {_channel_polling}
    outconn: {_outgoing_twilio}
    service: zato.ping
    receive_mode: polling
    scheduler_run_every: 30
    scheduler_run_unit: seconds

  - name: {_channel_webhook}
    outconn: {_outgoing_vonage}
    service: zato.ping
"""

# ################################################################################################################################
# ################################################################################################################################

def _by_name(items:'any_') -> 'stranydict':
    out = {}

    for item in items:
        out[item['name']] = item

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSMSExport(TestCase):
    """ Tests exporting outgoing SMS connection and SMS channel definitions to YAML format.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_sms.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()
        self.outgoing_importer = OutgoingSMSImporter(self.importer)
        self.channel_importer = ChannelSMSImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self):
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)
        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_outgoing_sms_export(self):
        self._setup_test_environment()

        sms_list_from_yaml = self.yaml_config['outgoing_sms']

        created, _ = self.outgoing_importer.sync_definitions(sms_list_from_yaml, self.session)
        self.assertEqual(len(created), 2)

        exported_data = self.exporter.export_to_dict(self.session)

        self.assertIn('outgoing_sms', exported_data)
        exported_sms_list = exported_data['outgoing_sms']
        self.assertEqual(len(exported_sms_list), 2)

        exported_by_name = _by_name(exported_sms_list)

        for yaml_def in sms_list_from_yaml:
            name = yaml_def['name']
            self.assertIn(name, exported_by_name)
            exported_def = exported_by_name[name]
            self.assertEqual(exported_def[SMS.Field_Provider], yaml_def[SMS.Field_Provider])
            self.assertEqual(exported_def[SMS.Field_Username], yaml_def[SMS.Field_Username])
            self.assertEqual(exported_def[SMS.Field_Sender], yaml_def[SMS.Field_Sender])

            # A secret is exported as a reference to an environment variable, never as its value
            self.assertTrue(exported_def[SMS.Field_Password].startswith(Env_Reference_Prefix))
            self.assertNotEqual(exported_def[SMS.Field_Password], yaml_def[SMS.Field_Password])

        twilio = exported_by_name[_outgoing_twilio]
        self.assertEqual(twilio[SMS.Field_Pool_Size], 5)
        self.assertNotIn('is_active', twilio)
        self.assertNotIn(SMS.Field_Signature_Secret, twilio)

        # Only the Vonage connection has a signature secret reference
        vonage = exported_by_name[_outgoing_vonage]
        self.assertFalse(vonage['is_active'])
        self.assertTrue(vonage[SMS.Field_Signature_Secret].startswith(Env_Reference_Prefix))

# ################################################################################################################################

    def test_channel_sms_export(self):
        self._setup_test_environment()

        _ = self.outgoing_importer.sync_definitions(self.yaml_config['outgoing_sms'], self.session)

        sms_list_from_yaml = self.yaml_config['channel_sms']

        # The importer replaces the file's `outconn` with the channel's own field name, so the names are kept beforehand
        outconn_by_name = {}
        for yaml_def in sms_list_from_yaml:
            outconn_by_name[yaml_def['name']] = yaml_def[Channel_Outconn_Key]

        created, _ = self.channel_importer.sync_definitions(sms_list_from_yaml, self.session)
        self.assertEqual(len(created), 2)

        exported_data = self.exporter.export_to_dict(self.session)

        self.assertIn('channel_sms', exported_data)
        exported_sms_list = exported_data['channel_sms']
        self.assertEqual(len(exported_sms_list), 2)

        exported_by_name = _by_name(exported_sms_list)

        for yaml_def in sms_list_from_yaml:
            name = yaml_def['name']
            self.assertIn(name, exported_by_name)
            exported_def = exported_by_name[name]
            self.assertEqual(exported_def[Channel_Outconn_Key], outconn_by_name[name])
            self.assertEqual(exported_def[SMS.Field_Service], yaml_def[SMS.Field_Service])

        # The polling channel exports its schedule and never its job ID ..
        polling = exported_by_name[_channel_polling]
        self.assertEqual(polling[SMS.Field_Receive_Mode], SMS.Receive_Mode.Polling)
        self.assertEqual(polling[_scheduler.Field_Run_Every], 30)
        self.assertEqual(polling[_scheduler.Field_Run_Unit], 'seconds')
        self.assertNotIn(_scheduler.Field_Job_ID, polling)

        # .. and the webhook one exports neither a receive mode nor a schedule.
        webhook = exported_by_name[_channel_webhook]
        self.assertNotIn(SMS.Field_Receive_Mode, webhook)
        self.assertNotIn(_scheduler.Field_Run_Every, webhook)
        self.assertNotIn(_scheduler.Field_Run_Unit, webhook)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging
    from unittest import main

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
