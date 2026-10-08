# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.sms import ChannelSMSImporter, OutgoingSMSImporter
from zato.cli.enmasse.util.secrets import decrypt_secret
from zato.common.api import GENERIC, SMS
from zato.common.odb.model import GenericConn, Job
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr

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

_twilio_password = 'enmasse.twilio.auth.token'
_vonage_signature_secret = 'enmasse.vonage.signature.secret'

template_sms = f"""
outgoing_sms:
  - name: {_outgoing_twilio}
    provider: twilio
    username: ACenmasse
    password: {_twilio_password}
    sender: '+12025550100'
    pool_size: 5

  - name: {_outgoing_vonage}
    is_active: false
    provider: vonage
    username: enmasse-vonage-key
    password: enmasse.vonage.api.secret
    signature_secret: {_vonage_signature_secret}
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

class _SMSTestCase(TestCase):

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_sms.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
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

    def _import_outgoing(self) -> 'tuple':
        out = self.outgoing_importer.sync_definitions(self.yaml_config['outgoing_sms'], self.session)
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingSMSFromYAML(_SMSTestCase):
    """ Tests importing outgoing SMS connection definitions from YAML files using enmasse.
    """

    def test_outgoing_sms_creation(self):
        self._setup_test_environment()

        created, updated = self._import_outgoing()

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        conn = self.session.query(GenericConn).filter_by(
            name=_outgoing_twilio,
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_SMS,
        ).one()
        opaque = parse_instance_opaque_attr(conn)

        self.assertTrue(conn.is_active)
        self.assertEqual(conn.username, 'ACenmasse')
        self.assertEqual(decrypt_secret(self.session, conn.secret), _twilio_password)

        self.assertEqual(opaque[SMS.Field_Provider], SMS.Provider.Twilio)
        self.assertEqual(opaque[SMS.Field_Host], SMS.Default_Host[SMS.Provider.Twilio])
        self.assertEqual(opaque[SMS.Field_Sender], '+12025550100')
        self.assertEqual(opaque[SMS.Field_Pool_Size], 5)
        self.assertNotIn(SMS.Field_Password, opaque)

# ################################################################################################################################

    def test_outgoing_sms_signature_secret(self) -> 'None':
        self._setup_test_environment()

        _ = self._import_outgoing()
        self.session.commit()

        conn = self.session.query(GenericConn).filter_by(
            name=_outgoing_vonage,
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_SMS,
        ).one()
        opaque = parse_instance_opaque_attr(conn)

        self.assertFalse(conn.is_active)
        self.assertNotEqual(opaque[SMS.Field_Signature_Secret], _vonage_signature_secret)
        self.assertEqual(decrypt_secret(self.session, opaque[SMS.Field_Signature_Secret]), _vonage_signature_secret)

# ################################################################################################################################

    def test_outgoing_sms_unknown_provider(self) -> 'None':
        self._setup_test_environment()

        sms_def = {
            'name': 'enmasse.sms.outgoing.unknown',
            'provider': 'carrier-pigeon',
            'username': 'enmasse',
            'password': 'enmasse',
            'sender': '+12025550102',
        }

        with self.assertRaises(Exception) as ctx:
            self.outgoing_importer.validate_definition(sms_def)

        self.assertIn('carrier-pigeon', str(ctx.exception))

# ################################################################################################################################

    def test_outgoing_sms_update(self):
        self._setup_test_environment()

        sms_defs = self.yaml_config['outgoing_sms']
        sms_def = sms_defs[0]

        instance = self.outgoing_importer.create_definition(sms_def, self.session)
        self.session.commit()
        self.assertEqual(instance.username, 'ACenmasse')

        update_def = {
            'name': sms_def['name'],
            'id': instance.id,
            'provider': 'twilio',
            'username': 'ACupdated',
            'sender': '+12025550103',
        }

        updated_instance = self.outgoing_importer.update_definition(update_def, self.session)
        self.session.commit()

        opaque = parse_instance_opaque_attr(updated_instance)

        self.assertEqual(updated_instance.username, 'ACupdated')
        self.assertEqual(opaque[SMS.Field_Sender], '+12025550103')

        # A password left out of the update keeps its stored value
        self.assertEqual(decrypt_secret(self.session, updated_instance.secret), _twilio_password)

# ################################################################################################################################

    def test_complete_outgoing_sms_import_flow(self):
        self._setup_test_environment()

        created, updated = self._import_outgoing()

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        created2, updated2 = self._import_outgoing()
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelSMSFromYAML(_SMSTestCase):
    """ Tests importing SMS channel definitions from YAML files using enmasse.
    """

    def test_channel_sms_creation(self):
        self._setup_test_environment()
        _ = self._import_outgoing()

        created, updated = self.channel_importer.sync_definitions(self.yaml_config['channel_sms'], self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        conn = self.session.query(GenericConn).filter_by(
            name=_channel_polling,
            type_=GENERIC.CONNECTION.TYPE.CHANNEL_SMS,
        ).one()
        opaque = parse_instance_opaque_attr(conn)

        self.assertTrue(conn.is_active)
        self.assertEqual(opaque[SMS.Field_Outconn_Name], _outgoing_twilio)
        self.assertEqual(opaque[SMS.Field_Service], 'zato.ping')
        self.assertEqual(opaque[SMS.Field_Receive_Mode], SMS.Receive_Mode.Polling)
        self.assertEqual(opaque[_scheduler.Field_Run_Every], 30)
        self.assertEqual(opaque[_scheduler.Field_Run_Unit], 'seconds')

# ################################################################################################################################

    def test_channel_sms_poll_job(self) -> 'None':
        self._setup_test_environment()
        _ = self._import_outgoing()
        _ = self.channel_importer.sync_definitions(self.yaml_config['channel_sms'], self.session)
        self.session.commit()

        # The polling channel has a job ..
        conn = self.session.query(GenericConn).filter_by(
            name=_channel_polling,
            type_=GENERIC.CONNECTION.TYPE.CHANNEL_SMS,
        ).one()
        opaque = parse_instance_opaque_attr(conn)

        job = self.session.query(Job).filter_by(name=_scheduler.Job_Prefix + _channel_polling).one()
        self.assertEqual(job.service.name, _scheduler.Dispatch_Service)
        self.assertEqual(job.interval_based.seconds, 30)
        self.assertEqual(opaque[_scheduler.Field_Job_ID], job.id)

        # .. and the webhook one has none.
        job = self.session.query(Job).filter_by(name=_scheduler.Job_Prefix + _channel_webhook).first()
        self.assertIsNone(job)

# ################################################################################################################################

    def test_channel_sms_unknown_outconn(self) -> 'None':
        self._setup_test_environment()
        _ = self._import_outgoing()

        sms_defs = self.yaml_config['channel_sms']
        sms_defs[0]['outconn'] = 'enmasse.sms.outgoing.missing'

        with self.assertRaises(Exception) as ctx:
            _ = self.channel_importer.sync_definitions(sms_defs, self.session)

        self.assertIn('enmasse.sms.outgoing.missing', str(ctx.exception))

# ################################################################################################################################

    def test_complete_channel_sms_import_flow(self):
        self._setup_test_environment()
        _ = self._import_outgoing()

        sms_list = self.yaml_config['channel_sms']
        created, updated = self.channel_importer.sync_definitions(sms_list, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        created2, updated2 = self.channel_importer.sync_definitions(sms_list, self.session)
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
