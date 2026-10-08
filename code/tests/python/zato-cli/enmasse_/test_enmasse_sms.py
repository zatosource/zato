# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Every field of an outgoing SMS connection and of an SMS channel through enmasse - the import for each of the four
# providers, each rejection the importers apply, an update that makes the YAML the source of truth, the polling job
# a channel creates and deletes, and the export that round trips through the writer with secrets as references.

# stdlib
from copy import deepcopy
from json import loads

# pytest
import pytest

# PyYAML
import yaml

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.exporters.sms import ChannelSMSExporter, Env_Reference_Prefix, OutgoingSMSExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.sms import Channel_Outconn_Key, ChannelSMSImporter, OutgoingSMSImporter
from zato.cli.enmasse.util import FileWriter
from zato.cli.enmasse.util.secrets import decrypt_secret, Session_Key_Crypto_Manager
from zato.common.api import HTTP_SOAP, SchedulerLink, SMS
from zato.common.crypto.api import ServerCryptoManager
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, IntervalBasedJob, Job, \
    SecurityBase, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anydict, stranydict

# ################################################################################################################################
# ################################################################################################################################

_scheduler = SMS.Scheduler
_retry = HTTP_SOAP.Retry
_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ

_cluster_id = 1

# One outgoing connection per provider - the Twilio one moves every field away from its default, the others
# have what each provider needs and nothing else
_outgoing_twilio = 'enmasse.sms.outgoing.twilio'
_outgoing_vonage = 'enmasse.sms.outgoing.vonage'
_outgoing_infobip = 'enmasse.sms.outgoing.infobip'
_outgoing_africas_talking = 'enmasse.sms.outgoing.africas-talking'

# One channel polls, the other receives webhooks and has only what it must
_channel_polling = 'enmasse.sms.channel.polling'
_channel_webhook = 'enmasse.sms.channel.webhook'

_service_name = 'enmasse.sms.service'
_forward_to = 'enmasse.sms.forward.topic'

_twilio_password = 'enmasse.twilio.auth.token'
_vonage_password = 'enmasse.vonage.api.secret'
_vonage_signature_secret = 'enmasse.vonage.signature.secret'
_infobip_password = 'enmasse.infobip.api.key'
_africas_talking_password = 'enmasse.africas.talking.api.key'

_infobip_host = 'https://abc123.api.infobip.com'

_yaml_text = f"""
outgoing_sms:
  - name: {_outgoing_twilio}
    provider: twilio
    host: https://api.twilio.example.com
    username: ACenmasse
    password: {_twilio_password}
    sender: '+12025550100'
    channel_name: enmasse-twilio
    pool_size: 5
    timeout: 15
    max_retries: 4
    retry_sleep_time: 5
    retry_backoff_threshold: 120
    retry_backoff_multiplier: 3
    use_queue: true
    use_dlq: false
    dlq_action: forward
    dlq_retries: 5
    dlq_retry_interval: 300
    dlq_forward_to: {_forward_to}
    dlq_keep_header: false

  - name: {_outgoing_vonage}
    provider: vonage
    username: enmasse-vonage-key
    password: {_vonage_password}
    signature_secret: {_vonage_signature_secret}
    sender: '+12025550101'

  - name: {_outgoing_infobip}
    provider: infobip
    host: {_infobip_host}
    username: enmasse-infobip
    password: {_infobip_password}
    sender: '+12025550102'

  - name: {_outgoing_africas_talking}
    provider: africas-talking
    username: sandbox
    password: {_africas_talking_password}
    sender: '+12025550103'

channel_sms:
  - name: {_channel_polling}
    outconn: {_outgoing_twilio}
    service: {_service_name}
    receive_mode: polling
    scheduler_run_every: 5
    scheduler_run_unit: seconds
    max_retries: 4
    retry_sleep_time: 5
    retry_backoff_threshold: 120
    retry_backoff_multiplier: 3
    use_queue: true
    use_dlq: false
    dlq_action: forward
    dlq_retries: 5
    dlq_retry_interval: 0
    dlq_forward_to: {_forward_to}
    dlq_keep_header: false

  - name: {_channel_webhook}
    outconn: {_outgoing_vonage}
    service: {_service_name}
"""

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def yaml_config() -> 'stranydict':
    out = yaml.safe_load(_yaml_text)
    return out

# ################################################################################################################################

@pytest.fixture
def session() -> 'any_':
    """ A real ODB session over an in-memory SQLite database holding one cluster and the service a polling job invokes,
    with the crypto manager the generic importer encrypts secrets with.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        GenericConnDef.__table__,
        GenericConn.__table__,
        GenericObject.__table__,
        Service.__table__,
        SecurityBase.__table__,
        Job.__table__,
        IntervalBasedJob.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    session.info[Session_Key_Crypto_Manager] = ServerCryptoManager.from_secret_key(ServerCryptoManager.generate_key())

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

    session.add(Service(None, _scheduler.Dispatch_Service, True, 'zato.server.service.internal.channel.sms.Poll', True, cluster))

    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def importer() -> 'EnmasseYAMLImporter':
    out = EnmasseYAMLImporter()
    return out

# ################################################################################################################################

@pytest.fixture
def outgoing_importer(importer:'EnmasseYAMLImporter') -> 'OutgoingSMSImporter':
    out = OutgoingSMSImporter(importer)
    return out

# ################################################################################################################################

@pytest.fixture
def channel_importer(importer:'EnmasseYAMLImporter') -> 'ChannelSMSImporter':
    out = ChannelSMSImporter(importer)
    return out

# ################################################################################################################################

@pytest.fixture
def outgoing_exporter() -> 'OutgoingSMSExporter':
    out = OutgoingSMSExporter(EnmasseYAMLExporter())
    return out

# ################################################################################################################################

@pytest.fixture
def channel_exporter() -> 'ChannelSMSExporter':
    out = ChannelSMSExporter(EnmasseYAMLExporter())
    return out

# ################################################################################################################################

def _opaque(connection:'any_') -> 'anydict':
    out = loads(connection.opaque1)
    return out

# ################################################################################################################################

def _by_name(items:'any_') -> 'anydict':
    out = {}

    for item in items:
        if isinstance(item, dict):
            out[item['name']] = item
        else:
            out[item.name] = item

    return out

# ################################################################################################################################

def _definitions(key:'str') -> 'any_':
    out = yaml.safe_load(_yaml_text)[key]
    return out

# ################################################################################################################################

def _import_outgoing(yaml_config:'stranydict', session:'any_', outgoing_importer:'OutgoingSMSImporter') -> 'anydict':
    created, _ = outgoing_importer.sync_definitions(yaml_config['outgoing_sms'], session)
    out = _by_name(created)
    return out

# ################################################################################################################################

def _assert_delivery_fields_moved(opaque:'anydict') -> 'None':
    """ The retry and DLQ fields the first connection of each kind moves away from the defaults.
    """
    assert opaque[_retry.Field_Max_Retries] == 4
    assert opaque[_retry.Field_Sleep_Time] == 5
    assert opaque[_retry.Field_Backoff_Threshold] == 120
    assert opaque[_retry.Field_Backoff_Multiplier] == 3

    assert opaque[_dlq.Field_Use_DLQ] is False
    assert opaque[_dlq.Field_Action] == _dlq.Action.Forward
    assert opaque[_dlq.Field_Retries] == 5
    assert opaque[_dlq.Field_Forward_To] == _forward_to
    assert opaque[_dlq.Field_Keep_Header] is False

# ################################################################################################################################

def _assert_delivery_defaults(opaque:'anydict') -> 'None':
    assert opaque[_retry.Field_Max_Retries] == _retry.Default_Max_Retries
    assert opaque[_retry.Field_Sleep_Time] == _retry.Default_Sleep_Time
    assert opaque[_retry.Field_Backoff_Threshold] == _retry.Default_Backoff_Threshold
    assert opaque[_retry.Field_Backoff_Multiplier] == _retry.Default_Backoff_Multiplier

    assert opaque[_dlq.Field_Use_DLQ] is _dlq.Default_Use_DLQ
    assert opaque[_dlq.Field_Action] == _dlq.Default_Action
    assert opaque[_dlq.Field_Retries] == _dlq.Default_Retries
    assert opaque[_dlq.Field_Retry_Interval] == _dlq.Default_Retry_Interval
    assert opaque[_dlq.Field_Forward_To] == _dlq.Default_Forward_To
    assert opaque[_dlq.Field_Keep_Header] is _dlq.Default_Keep_Header

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingSMSImport:

    def test_a_connection_stores_every_field(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
    ) -> 'None':
        connection = _import_outgoing(yaml_config, session, outgoing_importer)[_outgoing_twilio]
        opaque = _opaque(connection)

        assert connection.username == 'ACenmasse'
        assert connection.is_active is True

        # The password is stored encrypted in the secret column and never in the opaque attributes
        assert connection.secret != _twilio_password
        assert decrypt_secret(session, connection.secret) == _twilio_password
        assert SMS.Field_Password not in opaque
        assert SMS.Field_Secret not in opaque

        assert opaque[SMS.Field_Provider] == SMS.Provider.Twilio
        assert opaque[SMS.Field_Host] == 'https://api.twilio.example.com'
        assert opaque[SMS.Field_Sender] == '+12025550100'
        assert opaque[SMS.Field_Channel_Name] == 'enmasse-twilio'
        assert connection.pool_size == 5
        assert connection.timeout == 15

        assert opaque[_queue.Field_Use_Queue] is True
        assert opaque[_dlq.Field_Retry_Interval] == 300
        _assert_delivery_fields_moved(opaque)

# ################################################################################################################################

    def test_each_provider_imports_with_its_own_fields(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
    ) -> 'None':
        created = _import_outgoing(yaml_config, session, outgoing_importer)
        assert len(created) == 4

        # Vonage has a signature secret, stored encrypted in the opaque attributes ..
        vonage = created[_outgoing_vonage]
        opaque = _opaque(vonage)

        assert opaque[SMS.Field_Provider] == SMS.Provider.Vonage
        assert opaque[SMS.Field_Host] == SMS.Default_Host[SMS.Provider.Vonage]
        assert decrypt_secret(session, vonage.secret) == _vonage_password

        stored_signature_secret = opaque[SMS.Field_Signature_Secret]
        assert stored_signature_secret != _vonage_signature_secret
        assert decrypt_secret(session, stored_signature_secret) == _vonage_signature_secret

        # .. Infobip keeps the host it was given ..
        infobip = created[_outgoing_infobip]
        opaque = _opaque(infobip)

        assert opaque[SMS.Field_Provider] == SMS.Provider.Infobip
        assert opaque[SMS.Field_Host] == _infobip_host
        assert decrypt_secret(session, infobip.secret) == _infobip_password

        # .. and Africa's Talking runs on the defaults.
        africas_talking = created[_outgoing_africas_talking]
        opaque = _opaque(africas_talking)

        assert opaque[SMS.Field_Provider] == SMS.Provider.Africas_Talking
        assert opaque[SMS.Field_Host] == SMS.Default_Host[SMS.Provider.Africas_Talking]
        assert opaque[SMS.Field_Channel_Name] == ''
        assert africas_talking.pool_size == SMS.Default_Pool_Size
        assert africas_talking.timeout == SMS.Default_Timeout

        # A provider without a signature secret keeps the empty default, so the wrapper finds the key it expects
        assert opaque[SMS.Field_Signature_Secret] == ''
        assert decrypt_secret(session, africas_talking.secret) == _africas_talking_password

        assert opaque[_queue.Field_Use_Queue] is _queue.Default_Use_Queue
        _assert_delivery_defaults(opaque)

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
    ) -> 'None':
        created = _import_outgoing(yaml_config, session, outgoing_importer)
        assert len(created) == 4

        # A definition that drops its DLQ settings, its channel name and its password puts the connection
        # back on the defaults while the stored password stays ..
        definitions = _definitions('outgoing_sms')
        definitions[0][SMS.Field_Sender] = '+12025550199'

        del definitions[0][SMS.Field_Channel_Name]
        del definitions[0][SMS.Field_Password]

        for name in _dlq.FieldList:
            del definitions[0][name]

        created_again, updated = outgoing_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0

        connection = _by_name(updated)[_outgoing_twilio]
        opaque = _opaque(connection)

        assert opaque[SMS.Field_Sender] == '+12025550199'
        assert opaque[SMS.Field_Channel_Name] == ''
        assert decrypt_secret(session, connection.secret) == _twilio_password

        assert opaque[_dlq.Field_Use_DLQ] is _dlq.Default_Use_DLQ
        assert opaque[_dlq.Field_Action] == _dlq.Default_Action
        assert opaque[_dlq.Field_Retries] == _dlq.Default_Retries
        assert opaque[_dlq.Field_Forward_To] == _dlq.Default_Forward_To

        # .. the retry fields that stayed are still there ..
        assert opaque[_retry.Field_Max_Retries] == 4

        # .. and one that gains a new password has it.
        definitions[2][SMS.Field_Password] = 'enmasse.infobip.api.key.2'

        _, updated = outgoing_importer.sync_definitions(definitions, session)
        connection = _by_name(updated)[_outgoing_infobip]

        assert decrypt_secret(session, connection.secret) == 'enmasse.infobip.api.key.2'

# ################################################################################################################################

    def test_an_unknown_provider_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_sms']
        definitions[0][SMS.Field_Provider] = 'carrier-pigeon'

        with pytest.raises(Exception) as context:
            _ = outgoing_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'carrier-pigeon' in message
        assert _outgoing_twilio in message

# ################################################################################################################################

    def test_a_signature_secret_on_a_provider_without_one_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_sms']
        definitions[0][SMS.Field_Signature_Secret] = 'not-for-twilio'

        with pytest.raises(Exception) as context:
            _ = outgoing_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'signature secret' in message
        assert _outgoing_twilio in message

# ################################################################################################################################

    def test_an_infobip_connection_without_a_host_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_sms']
        del definitions[2][SMS.Field_Host]

        with pytest.raises(Exception) as context:
            _ = outgoing_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'requires a host' in message
        assert _outgoing_infobip in message

# ################################################################################################################################

    def test_a_negative_count_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_sms']
        definitions[0][SMS.Field_Timeout] = -1

        with pytest.raises(Exception) as context:
            _ = outgoing_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert SMS.Field_Timeout in message
        assert 'negative' in message

# ################################################################################################################################
# ################################################################################################################################

class TestChannelSMSImport:

    def test_a_polling_channel_stores_every_field_and_creates_its_job(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
        channel_importer:'ChannelSMSImporter',
    ) -> 'None':
        _ = _import_outgoing(yaml_config, session, outgoing_importer)

        created, _ = channel_importer.sync_definitions(yaml_config['channel_sms'], session)
        connection = _by_name(created)[_channel_polling]
        opaque = _opaque(connection)

        # The file's `outconn` is stored under the channel's own field name
        assert opaque[SMS.Field_Outconn_Name] == _outgoing_twilio
        assert Channel_Outconn_Key not in opaque

        assert opaque[SMS.Field_Service] == _service_name
        assert opaque[SMS.Field_Receive_Mode] == SMS.Receive_Mode.Polling
        assert opaque[_scheduler.Field_Run_Every] == 5
        assert opaque[_scheduler.Field_Run_Unit] == 'seconds'

        # The queue switch is the file's, and an interval of zero is allowed
        assert opaque[_queue.Field_Use_Queue] is True
        assert opaque[_dlq.Field_Retry_Interval] == 0
        _assert_delivery_fields_moved(opaque)

        # The job exists, named after the channel, invoking the poll service on the schedule asked for ..
        job = session.query(Job).filter_by(name=_scheduler.Job_Prefix + _channel_polling).one()
        assert job.service.name == _scheduler.Dispatch_Service
        assert job.is_active is True
        assert job.interval_based.seconds == 5

        job_opaque = loads(job.opaque1)
        assert job_opaque[SchedulerLink.Conn_Type] == SchedulerLink.ConnType.SMS_Channel
        assert job_opaque[SchedulerLink.Conn_ID] == connection.id
        assert job_opaque[SchedulerLink.Kind] == SchedulerLink.KindType.Scheduler

        extra = loads(job.extra)
        assert extra[_scheduler.Extra_Conn_ID] == connection.id
        assert extra[_scheduler.Extra_Conn_Name] == _channel_polling

        # .. and the channel remembers the job.
        assert opaque[_scheduler.Field_Job_ID] == job.id

        # The same file again finds the job by its name rather than creating another
        _, _ = channel_importer.sync_definitions(_definitions('channel_sms'), session)
        assert session.query(Job).filter_by(name=_scheduler.Job_Prefix + _channel_polling).count() == 1

# ################################################################################################################################

    def test_a_webhook_channel_runs_on_defaults_without_a_job(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
        channel_importer:'ChannelSMSImporter',
    ) -> 'None':
        _ = _import_outgoing(yaml_config, session, outgoing_importer)

        created, _ = channel_importer.sync_definitions(yaml_config['channel_sms'], session)
        connection = _by_name(created)[_channel_webhook]
        opaque = _opaque(connection)

        assert opaque[SMS.Field_Outconn_Name] == _outgoing_vonage
        assert opaque[SMS.Field_Receive_Mode] == SMS.Receive_Mode.Webhook
        assert opaque[_scheduler.Field_Run_Every] == _scheduler.Default_Run_Every
        assert opaque[_scheduler.Field_Run_Unit] == _scheduler.Default_Run_Unit
        assert opaque[_scheduler.Field_Job_ID] == 0

        assert opaque[_queue.Field_Use_Queue] is _queue.Default_Use_Queue
        _assert_delivery_defaults(opaque)

        assert session.query(Job).filter_by(name=_scheduler.Job_Prefix + _channel_webhook).first() is None

# ################################################################################################################################

    def test_a_change_of_receive_mode_creates_and_deletes_the_job(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
        channel_importer:'ChannelSMSImporter',
    ) -> 'None':
        _ = _import_outgoing(yaml_config, session, outgoing_importer)
        _, _ = channel_importer.sync_definitions(yaml_config['channel_sms'], session)

        # The polling channel turns to webhooks and loses its job ..
        definitions = _definitions('channel_sms')
        definitions[0][SMS.Field_Receive_Mode] = SMS.Receive_Mode.Webhook

        # .. while the webhook one starts polling on the default schedule and gains one.
        definitions[1][SMS.Field_Receive_Mode] = SMS.Receive_Mode.Polling

        _, updated = channel_importer.sync_definitions(definitions, session)
        updated = _by_name(updated)

        assert session.query(Job).filter_by(name=_scheduler.Job_Prefix + _channel_polling).first() is None
        assert _opaque(updated[_channel_polling])[_scheduler.Field_Job_ID] == 0

        job = session.query(Job).filter_by(name=_scheduler.Job_Prefix + _channel_webhook).one()
        assert job.interval_based.minutes == _scheduler.Default_Run_Every
        assert _opaque(updated[_channel_webhook])[_scheduler.Field_Job_ID] == job.id

# ################################################################################################################################

    def test_a_channel_naming_an_unknown_outgoing_connection_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
        channel_importer:'ChannelSMSImporter',
    ) -> 'None':
        _ = _import_outgoing(yaml_config, session, outgoing_importer)

        definitions = yaml_config['channel_sms']
        definitions[0][Channel_Outconn_Key] = 'enmasse.sms.outgoing.missing'

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'enmasse.sms.outgoing.missing' in message
        assert _channel_polling in message

# ################################################################################################################################

    def test_a_channel_without_a_service_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
        channel_importer:'ChannelSMSImporter',
    ) -> 'None':
        _ = _import_outgoing(yaml_config, session, outgoing_importer)

        definitions = yaml_config['channel_sms']
        del definitions[1][SMS.Field_Service]

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'requires a service' in message
        assert _channel_webhook in message

# ################################################################################################################################

    def test_an_unknown_receive_mode_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
        channel_importer:'ChannelSMSImporter',
    ) -> 'None':
        _ = _import_outgoing(yaml_config, session, outgoing_importer)

        definitions = yaml_config['channel_sms']
        definitions[0][SMS.Field_Receive_Mode] = 'carrier-pigeon'

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'carrier-pigeon' in message
        assert SMS.Receive_Mode.Polling in message

# ################################################################################################################################
# ################################################################################################################################

class TestSMSExport:

    def test_an_outgoing_connection_exports_every_field_with_secrets_as_references(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
        outgoing_exporter:'OutgoingSMSExporter',
    ) -> 'None':
        _ = _import_outgoing(yaml_config, session, outgoing_importer)

        exported = _by_name(outgoing_exporter.export(session, _cluster_id))
        item = exported[_outgoing_twilio]

        assert item[SMS.Field_Provider] == SMS.Provider.Twilio
        assert item[SMS.Field_Host] == 'https://api.twilio.example.com'
        assert item[SMS.Field_Username] == 'ACenmasse'
        assert item[SMS.Field_Sender] == '+12025550100'
        assert item[SMS.Field_Channel_Name] == 'enmasse-twilio'
        assert item[SMS.Field_Pool_Size] == 5
        assert item[SMS.Field_Timeout] == 15

        assert item[_retry.Field_Max_Retries] == 4
        assert item[_queue.Field_Use_Queue] is True
        assert item[_dlq.Field_Use_DLQ] is False
        assert item[_dlq.Field_Action] == _dlq.Action.Forward
        assert item[_dlq.Field_Retries] == 5
        assert item[_dlq.Field_Retry_Interval] == 300
        assert item[_dlq.Field_Forward_To] == _forward_to
        assert item[_dlq.Field_Keep_Header] is False

        # A secret never leaves in clear text - the file refers to it through an environment variable
        assert item[SMS.Field_Password] == Env_Reference_Prefix + 'SMS_enmasse_sms_outgoing_twilio_Password'
        assert SMS.Field_Signature_Secret not in item

        # Only a Vonage connection has a signature secret reference
        item = exported[_outgoing_vonage]
        assert item[SMS.Field_Password] == Env_Reference_Prefix + 'SMS_enmasse_sms_outgoing_vonage_Password'
        assert item[SMS.Field_Signature_Secret] == Env_Reference_Prefix + 'SMS_enmasse_sms_outgoing_vonage_Signature_Secret'

        # The connection on defaults exports only what it must
        item = exported[_outgoing_africas_talking]
        assert item == {
            'name': _outgoing_africas_talking,
            SMS.Field_Provider: SMS.Provider.Africas_Talking,
            SMS.Field_Host: SMS.Default_Host[SMS.Provider.Africas_Talking],
            SMS.Field_Username: 'sandbox',
            SMS.Field_Sender: '+12025550103',
            SMS.Field_Password: Env_Reference_Prefix + 'SMS_enmasse_sms_outgoing_africas_talking_Password',
        }

# ################################################################################################################################

    def test_a_channel_exports_every_field_moved_away_from_its_default(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
        channel_importer:'ChannelSMSImporter',
        channel_exporter:'ChannelSMSExporter',
    ) -> 'None':
        _ = _import_outgoing(yaml_config, session, outgoing_importer)
        _, _ = channel_importer.sync_definitions(yaml_config['channel_sms'], session)

        exported = _by_name(channel_exporter.export(session, _cluster_id))
        item = exported[_channel_polling]

        assert item[Channel_Outconn_Key] == _outgoing_twilio
        assert SMS.Field_Outconn_Name not in item

        assert item[SMS.Field_Service] == _service_name
        assert item[SMS.Field_Receive_Mode] == SMS.Receive_Mode.Polling
        assert item[_scheduler.Field_Run_Every] == 5
        assert item[_scheduler.Field_Run_Unit] == 'seconds'

        # A job ID is environment-local and never exported
        assert _scheduler.Field_Job_ID not in item

        assert item[_retry.Field_Max_Retries] == 4
        assert item[_dlq.Field_Use_DLQ] is False
        assert item[_dlq.Field_Action] == _dlq.Action.Forward
        assert item[_dlq.Field_Retry_Interval] == 0
        assert item[_dlq.Field_Forward_To] == _forward_to

        # The queue switch moved away from its default, so it is written
        assert item[_queue.Field_Use_Queue] is True

        # The webhook channel exports only what it must, and no schedule
        item = exported[_channel_webhook]
        assert item == {
            'name': _channel_webhook,
            Channel_Outconn_Key: _outgoing_vonage,
            SMS.Field_Service: _service_name,
        }

# ################################################################################################################################

    def test_the_export_round_trips_through_the_writer(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingSMSImporter',
        channel_importer:'ChannelSMSImporter',
        outgoing_exporter:'OutgoingSMSExporter',
        channel_exporter:'ChannelSMSExporter',
        tmp_path:'Path',
    ) -> 'None':
        _ = _import_outgoing(yaml_config, session, outgoing_importer)
        _, _ = channel_importer.sync_definitions(yaml_config['channel_sms'], session)

        exported_outgoing = outgoing_exporter.export(session, _cluster_id)
        exported_channels = channel_exporter.export(session, _cluster_id)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'outgoing_sms': exported_outgoing, 'channel_sms': exported_channels})

        written = path.read_text()
        read_back = yaml.safe_load(written)

        assert read_back['outgoing_sms'] == exported_outgoing
        assert read_back['channel_sms'] == exported_channels

        # What was exported imports as itself - nothing is created, and a secret reference whose environment
        # variable is not set keeps the stored secret. The importer works on a copy because it rewrites
        # the definitions it is given.
        created, updated = outgoing_importer.sync_definitions(deepcopy(read_back['outgoing_sms']), session)
        assert len(created) == 0

        connection = _by_name(updated)[_outgoing_twilio]
        assert decrypt_secret(session, connection.secret) == _twilio_password

        connection = _by_name(updated)[_outgoing_vonage]
        assert decrypt_secret(session, _opaque(connection)[SMS.Field_Signature_Secret]) == _vonage_signature_secret

        created, _ = channel_importer.sync_definitions(deepcopy(read_back['channel_sms']), session)
        assert len(created) == 0

        # A second export is the same as the first
        assert outgoing_exporter.export(session, _cluster_id) == exported_outgoing
        assert channel_exporter.export(session, _cluster_id) == exported_channels

# ################################################################################################################################
# ################################################################################################################################
