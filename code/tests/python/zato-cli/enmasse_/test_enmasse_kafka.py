# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Every field of a Kafka channel and of an outgoing Kafka connection through enmasse - the import, an update
# that makes the YAML the source of truth, and the export that round trips through the writer.

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
from zato.cli.enmasse.exporters.kafka import ChannelKafkaExporter, OutgoingKafkaExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.kafka import ChannelKafkaImporter, OutgoingKafkaImporter
from zato.cli.enmasse.util import FileWriter
from zato.cli.enmasse.util.secrets import decrypt_secret, Session_Key_Crypto_Manager
from zato.common.api import HTTP_SOAP, KAFKA, SEC_DEF_TYPE
from zato.common.crypto.api import ServerCryptoManager
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, SecurityBase, Service, SMTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anydict, stranydict

# ################################################################################################################################
# ################################################################################################################################

_consumer = KAFKA.Consumer
_producer = KAFKA.Producer
_routing = KAFKA.Routing
_retry = HTTP_SOAP.Retry
_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ

_cluster_id = 1

# The security definition the SASL connections name, known to the importer as a Basic Auth one
_security_name = 'enmasse.kafka.basic'
_security_id = 1234

# One connection of each kind moves every field away from its default, the other carries only what it must
_channel_name_1 = 'enmasse.kafka.channel.1'
_channel_name_2 = 'enmasse.kafka.channel.2'
_outgoing_name_1 = 'enmasse.kafka.outgoing.1'
_outgoing_name_2 = 'enmasse.kafka.outgoing.2'

# A channel from a file written before the topic list existed
_channel_name_legacy = 'enmasse.kafka.channel.legacy'

_forward_to = 'enmasse.kafka.forward.topic'
_key_password = 'enmasse.kafka.key.password'

_yaml_text = f"""
channel_kafka:
  - name: {_channel_name_1}
    address: kafka1:9092,kafka2:9092
    topics:
      - orders
      - invoices
    group_id: enmasse-group
    service: enmasse.kafka.service
    auto_offset_reset: earliest
    max_message_size: 2000000
    max_in_flight: 50
    should_deliver_tombstones: true
    dedup_header: msg-id
    dedup_ttl: 3600
    routing:
      - topic: invoices
        service: enmasse.kafka.invoices
      - header_name: kind
        header_value: urgent
        service: enmasse.kafka.urgent
    max_retries: 4
    retry_sleep_time: 5
    retry_backoff_threshold: 120
    retry_backoff_multiplier: 3
    use_dlq: false
    dlq_action: forward
    dlq_retries: 5
    dlq_retry_interval: 0
    dlq_forward_to: {_forward_to}
    dlq_keep_header: false
    ssl: true
    ssl_ca_file: /etc/kafka/ca.crt
    ssl_cert_file: /etc/kafka/client.crt
    ssl_key_file: /etc/kafka/client.key
    ssl_key_password: {_key_password}
    security: {_security_name}
    sasl_mechanism: PLAIN

  - name: {_channel_name_2}
    address: kafka3:9092
    topics:
      - events
    service: enmasse.kafka.service

  - name: {_channel_name_legacy}
    address: kafka3:9092
    topic: legacy
    service: enmasse.kafka.service

outgoing_kafka:
  - name: {_outgoing_name_1}
    address: kafka1:9092,kafka2:9092
    topic: outbound
    compression: zstd
    acks: 1
    is_idempotent: false
    max_message_size: 3000000
    linger_ms: 25
    send_timeout: 15
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
    ssl: true
    ssl_ca_file: /etc/kafka/ca.crt
    ssl_cert_file: /etc/kafka/client.crt
    ssl_key_file: /etc/kafka/client.key
    ssl_key_password: {_key_password}
    security: {_security_name}
    sasl_mechanism: PLAIN

  - name: {_outgoing_name_2}
    address: kafka3:9092
    topic: outbound
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
    """ A real ODB session over an in-memory SQLite database holding one cluster, carrying the crypto manager
    the generic importer encrypts secrets with.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        GenericConnDef.__table__,
        GenericConn.__table__,
        GenericObject.__table__,
        SMTP.__table__,
        Service.__table__,
        SecurityBase.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    session.info[Session_Key_Crypto_Manager] = ServerCryptoManager.from_secret_key(ServerCryptoManager.generate_key())

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)
    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def importer() -> 'EnmasseYAMLImporter':
    """ The importer with the one security definition the connections refer to.
    """
    out = EnmasseYAMLImporter()
    out.sec_defs[_security_name] = {'id': _security_id, 'name': _security_name, 'type': SEC_DEF_TYPE.BASIC_AUTH}

    return out

# ################################################################################################################################

@pytest.fixture
def channel_importer(importer:'EnmasseYAMLImporter') -> 'ChannelKafkaImporter':
    out = ChannelKafkaImporter(importer)
    return out

# ################################################################################################################################

@pytest.fixture
def outgoing_importer(importer:'EnmasseYAMLImporter') -> 'OutgoingKafkaImporter':
    out = OutgoingKafkaImporter(importer)
    return out

# ################################################################################################################################

@pytest.fixture
def channel_exporter() -> 'ChannelKafkaExporter':
    out = ChannelKafkaExporter(EnmasseYAMLExporter())
    return out

# ################################################################################################################################

@pytest.fixture
def outgoing_exporter() -> 'OutgoingKafkaExporter':
    out = OutgoingKafkaExporter(EnmasseYAMLExporter())
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

def _assert_common_fields(opaque:'anydict', session:'any_') -> 'None':
    """ The retry, SSL and security fields both kinds of connection store the same way.
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

    assert opaque['ssl'] is True
    assert opaque['ssl_ca_file'] == '/etc/kafka/ca.crt'
    assert opaque['ssl_cert_file'] == '/etc/kafka/client.crt'
    assert opaque['ssl_key_file'] == '/etc/kafka/client.key'

    # The key password is stored encrypted and never in clear text
    stored_password = opaque[KAFKA.Field_SSL_Key_Password]
    assert stored_password != _key_password
    assert decrypt_secret(session, stored_password) == _key_password

    assert opaque['sasl_mechanism'] == 'PLAIN'
    assert opaque['security_name'] == _security_name
    assert opaque['auth_type'] == SEC_DEF_TYPE.BASIC_AUTH

# ################################################################################################################################
# ################################################################################################################################

class TestChannelKafkaImport:

    def test_a_channel_stores_every_field(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelKafkaImporter',
    ) -> 'None':
        created, _ = channel_importer.sync_definitions(yaml_config['channel_kafka'], session)
        connection = _by_name(created)[_channel_name_1]

        opaque = _opaque(connection)

        assert connection.address == 'kafka1:9092,kafka2:9092'
        assert opaque['security_id'] == _security_id

        # The topics are stored one per line and the first one is the topic
        assert opaque[_consumer.Field_Topics] == 'orders\ninvoices'
        assert opaque['topic'] == 'orders'

        assert opaque['group_id'] == 'enmasse-group'
        assert opaque['service'] == 'enmasse.kafka.service'
        assert opaque[_consumer.Field_Auto_Offset_Reset] == 'earliest'
        assert opaque[_consumer.Field_Max_Message_Size] == 2000000
        assert opaque[_consumer.Field_Max_In_Flight] == 50
        assert opaque[_consumer.Field_Should_Deliver_Tombstones] is True
        assert opaque[_consumer.Field_Dedup_Header] == 'msg-id'
        assert opaque[_consumer.Field_Dedup_TTL] == 3600

        # The routing rules are stored as JSON with every key of a rule present
        rules = loads(opaque[_consumer.Field_Routing])
        assert rules == [
            {_routing.Key_Topic: 'invoices', _routing.Key_Header_Name: '', _routing.Key_Header_Value: '',
                _routing.Key_Service: 'enmasse.kafka.invoices'},
            {_routing.Key_Topic: '', _routing.Key_Header_Name: 'kind', _routing.Key_Header_Value: 'urgent',
                _routing.Key_Service: 'enmasse.kafka.urgent'},
        ]

        # A channel has no queue, and an interval of zero is allowed
        assert opaque[_queue.Field_Use_Queue] is False
        assert opaque[_dlq.Field_Retry_Interval] == 0

        _assert_common_fields(opaque, session)

# ################################################################################################################################

    def test_a_channel_without_the_settings_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelKafkaImporter',
    ) -> 'None':
        created, _ = channel_importer.sync_definitions(yaml_config['channel_kafka'], session)
        connection = _by_name(created)[_channel_name_2]

        opaque = _opaque(connection)

        assert opaque[_consumer.Field_Topics] == 'events'
        assert opaque['topic'] == 'events'
        assert opaque['group_id'] == ''
        assert opaque[_consumer.Field_Routing] == ''

        for name, default in _consumer.Defaults.items():
            if name not in (_consumer.Field_Topics, _consumer.Field_Routing):
                assert opaque[name] == default, name

        assert opaque[_retry.Field_Max_Retries] == _retry.Default_Max_Retries
        assert opaque[_retry.Field_Sleep_Time] == _retry.Default_Sleep_Time
        assert opaque[_retry.Field_Backoff_Threshold] == _retry.Default_Backoff_Threshold
        assert opaque[_retry.Field_Backoff_Multiplier] == _retry.Default_Backoff_Multiplier

        assert opaque[_queue.Field_Use_Queue] is False
        assert opaque[_dlq.Field_Use_DLQ] is _dlq.Default_Use_DLQ
        assert opaque[_dlq.Field_Action] == _dlq.Default_Action
        assert opaque[_dlq.Field_Retries] == _dlq.Default_Retries
        assert opaque[_dlq.Field_Retry_Interval] == _dlq.Default_Retry_Interval
        assert opaque[_dlq.Field_Forward_To] == _dlq.Default_Forward_To
        assert opaque[_dlq.Field_Keep_Header] is _dlq.Default_Keep_Header

        assert opaque['ssl'] is False
        assert opaque['ssl_ca_file'] is None
        assert opaque['sasl_mechanism'] == ''
        assert 'security_id' not in opaque

# ################################################################################################################################

    def test_a_legacy_topic_is_a_one_entry_list(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelKafkaImporter',
    ) -> 'None':
        created, _ = channel_importer.sync_definitions(yaml_config['channel_kafka'], session)
        connection = _by_name(created)[_channel_name_legacy]

        opaque = _opaque(connection)

        assert opaque[_consumer.Field_Topics] == 'legacy'
        assert opaque['topic'] == 'legacy'

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelKafkaImporter',
    ) -> 'None':
        created, _ = channel_importer.sync_definitions(yaml_config['channel_kafka'], session)
        assert len(created) == 3

        # A definition that drops its routing, its DLQ settings and its consumer settings puts the channel back on
        # the defaults, and one that changes its topics has the new list ..
        definitions = _definitions('channel_kafka')
        definitions[0][_consumer.Field_Topics] = ['orders', 'returns', 'invoices']

        del definitions[0][_consumer.Field_Routing]
        del definitions[0][_consumer.Field_Dedup_Header]
        del definitions[0][_consumer.Field_Should_Deliver_Tombstones]

        for name in _dlq.FieldList:
            del definitions[0][name]

        created_again, updated = channel_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0

        connection = _by_name(updated)[_channel_name_1]
        opaque = _opaque(connection)

        assert opaque[_consumer.Field_Topics] == 'orders\nreturns\ninvoices'
        assert opaque['topic'] == 'orders'
        assert opaque[_consumer.Field_Routing] == ''
        assert opaque[_consumer.Field_Dedup_Header] == ''
        assert opaque[_consumer.Field_Should_Deliver_Tombstones] is False

        assert opaque[_dlq.Field_Use_DLQ] is True
        assert opaque[_dlq.Field_Action] == _dlq.Action.Keep
        assert opaque[_dlq.Field_Retries] == 3
        assert opaque[_dlq.Field_Retry_Interval] == 60
        assert opaque[_dlq.Field_Forward_To] == ''
        assert opaque[_dlq.Field_Keep_Header] is True

        # .. the retry fields that stayed are still there ..
        assert opaque[_retry.Field_Max_Retries] == 4

        # .. a password left out of the update keeps its stored value ..
        assert decrypt_secret(session, opaque[KAFKA.Field_SSL_Key_Password]) == _key_password

        # .. and one that gains settings gains them.
        definitions[1][_consumer.Field_Dedup_Header] = 'event-id'
        definitions[1][_dlq.Field_Action] = _dlq.Action.Discard

        _, updated = channel_importer.sync_definitions(definitions, session)

        connection = _by_name(updated)[_channel_name_2]
        opaque = _opaque(connection)

        assert opaque[_consumer.Field_Dedup_Header] == 'event-id'
        assert opaque[_dlq.Field_Action] == _dlq.Action.Discard

# ################################################################################################################################

    def test_a_channel_without_a_topic_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelKafkaImporter',
    ) -> 'None':
        definitions = yaml_config['channel_kafka']
        del definitions[1][_consumer.Field_Topics]

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'at least one topic' in message
        assert _channel_name_2 in message

# ################################################################################################################################

    def test_a_routing_rule_without_a_service_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelKafkaImporter',
    ) -> 'None':
        definitions = yaml_config['channel_kafka']
        definitions[0][_consumer.Field_Routing] = [{_routing.Key_Topic: 'orders'}]

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'needs a service' in message
        assert _channel_name_1 in message

# ################################################################################################################################

    def test_an_unknown_offset_reset_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelKafkaImporter',
    ) -> 'None':
        definitions = yaml_config['channel_kafka']
        definitions[0][_consumer.Field_Auto_Offset_Reset] = 'middle'

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'middle' in message
        assert 'earliest' in message

# ################################################################################################################################

    def test_a_sasl_mechanism_without_a_security_definition_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelKafkaImporter',
    ) -> 'None':
        definitions = yaml_config['channel_kafka']
        del definitions[0]['security']

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'no security definition' in message
        assert _channel_name_1 in message

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingKafkaImport:

    def test_a_connection_stores_every_field(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingKafkaImporter',
    ) -> 'None':
        created, _ = outgoing_importer.sync_definitions(yaml_config['outgoing_kafka'], session)
        connection = _by_name(created)[_outgoing_name_1]

        opaque = _opaque(connection)

        assert connection.address == 'kafka1:9092,kafka2:9092'
        assert opaque['security_id'] == _security_id

        assert opaque['topic'] == 'outbound'
        assert opaque[_producer.Field_Compression] == 'zstd'

        # The confirmation level is stored as text, however the YAML spelled it
        assert opaque[_producer.Field_Acks] == '1'

        assert opaque[_producer.Field_Is_Idempotent] is False
        assert opaque[_producer.Field_Max_Message_Size] == 3000000
        assert opaque[_producer.Field_Linger_Ms] == 25
        assert opaque[_producer.Field_Send_Timeout] == 15

        assert opaque[_queue.Field_Use_Queue] is True
        assert opaque[_dlq.Field_Retry_Interval] == 300

        _assert_common_fields(opaque, session)

# ################################################################################################################################

    def test_a_connection_without_the_settings_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingKafkaImporter',
    ) -> 'None':
        created, _ = outgoing_importer.sync_definitions(yaml_config['outgoing_kafka'], session)
        connection = _by_name(created)[_outgoing_name_2]

        opaque = _opaque(connection)

        for name, default in _producer.Defaults.items():
            assert opaque[name] == default, name

        assert opaque[_queue.Field_Use_Queue] is False
        assert opaque[_dlq.Field_Use_DLQ] is True
        assert opaque[_dlq.Field_Action] == _dlq.Action.Keep
        assert opaque['ssl'] is False
        assert 'security_id' not in opaque

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingKafkaImporter',
    ) -> 'None':
        created, _ = outgoing_importer.sync_definitions(yaml_config['outgoing_kafka'], session)
        assert len(created) == 2

        definitions = _definitions('outgoing_kafka')

        del definitions[0][_producer.Field_Compression]
        del definitions[0][_producer.Field_Acks]
        del definitions[0][_producer.Field_Is_Idempotent]

        for name in _dlq.FieldList:
            del definitions[0][name]

        created_again, updated = outgoing_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0

        connection = _by_name(updated)[_outgoing_name_1]
        opaque = _opaque(connection)

        assert opaque[_producer.Field_Compression] == _producer.Default_Compression
        assert opaque[_producer.Field_Acks] == _producer.Default_Acks
        assert opaque[_producer.Field_Is_Idempotent] is True

        assert opaque[_queue.Field_Use_Queue] is True
        assert opaque[_dlq.Field_Use_DLQ] is True
        assert opaque[_dlq.Field_Action] == _dlq.Action.Keep

        assert decrypt_secret(session, opaque[KAFKA.Field_SSL_Key_Password]) == _key_password

        definitions[1][_producer.Field_Acks] = 0
        definitions[1][_queue.Field_Use_Queue] = True

        _, updated = outgoing_importer.sync_definitions(definitions, session)

        connection = _by_name(updated)[_outgoing_name_2]
        opaque = _opaque(connection)

        assert opaque[_producer.Field_Acks] == '0'
        assert opaque[_queue.Field_Use_Queue] is True

# ################################################################################################################################

    def test_an_unknown_compression_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingKafkaImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_kafka']
        definitions[0][_producer.Field_Compression] = 'brotli'

        with pytest.raises(Exception) as context:
            _ = outgoing_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'brotli' in message
        assert 'zstd' in message

# ################################################################################################################################

    def test_an_unknown_confirmation_level_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingKafkaImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_kafka']
        definitions[0][_producer.Field_Acks] = 2

        with pytest.raises(Exception) as context:
            _ = outgoing_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert "'2'" in message
        assert 'all' in message

# ################################################################################################################################

    def test_a_negative_count_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingKafkaImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_kafka']
        definitions[0][_producer.Field_Linger_Ms] = -1

        with pytest.raises(Exception) as context:
            _ = outgoing_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert _producer.Field_Linger_Ms in message
        assert 'negative' in message

# ################################################################################################################################
# ################################################################################################################################

class TestKafkaExport:

    def test_a_channel_exports_every_field_moved_away_from_its_default(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelKafkaImporter',
        channel_exporter:'ChannelKafkaExporter',
    ) -> 'None':
        _, _ = channel_importer.sync_definitions(yaml_config['channel_kafka'], session)

        exported = channel_exporter.export(session, _cluster_id)
        item = _by_name(exported)[_channel_name_1]

        assert item['address'] == 'kafka1:9092,kafka2:9092'
        assert item[_consumer.Field_Topics] == ['orders', 'invoices']
        assert 'topic' not in item

        assert item['group_id'] == 'enmasse-group'
        assert item['service'] == 'enmasse.kafka.service'
        assert item[_consumer.Field_Auto_Offset_Reset] == 'earliest'
        assert item[_consumer.Field_Max_Message_Size] == 2000000
        assert item[_consumer.Field_Max_In_Flight] == 50
        assert item[_consumer.Field_Should_Deliver_Tombstones] is True
        assert item[_consumer.Field_Dedup_Header] == 'msg-id'
        assert item[_consumer.Field_Dedup_TTL] == 3600

        # A rule carries only the keys it sets
        assert item[_consumer.Field_Routing] == [
            {_routing.Key_Topic: 'invoices', _routing.Key_Service: 'enmasse.kafka.invoices'},
            {_routing.Key_Header_Name: 'kind', _routing.Key_Header_Value: 'urgent', _routing.Key_Service: 'enmasse.kafka.urgent'},
        ]

        assert item[_retry.Field_Max_Retries] == 4
        assert item[_retry.Field_Sleep_Time] == 5
        assert item[_retry.Field_Backoff_Threshold] == 120
        assert item[_retry.Field_Backoff_Multiplier] == 3

        assert item[_dlq.Field_Use_DLQ] is False
        assert item[_dlq.Field_Action] == _dlq.Action.Forward
        assert item[_dlq.Field_Retries] == 5
        assert item[_dlq.Field_Retry_Interval] == 0
        assert item[_dlq.Field_Forward_To] == _forward_to
        assert item[_dlq.Field_Keep_Header] is False

        # A channel never has a queue, so the switch is never written
        assert _queue.Field_Use_Queue not in item

        assert item['ssl'] is True
        assert item['ssl_ca_file'] == '/etc/kafka/ca.crt'
        assert item['ssl_cert_file'] == '/etc/kafka/client.crt'
        assert item['ssl_key_file'] == '/etc/kafka/client.key'

        # A secret never leaves through an export
        assert KAFKA.Field_SSL_Key_Password not in item

        assert item['security'] == _security_name
        assert item['sasl_mechanism'] == 'PLAIN'

        # The channel on defaults exports only what it must
        item = _by_name(exported)[_channel_name_2]
        assert item == {
            'name': _channel_name_2,
            'address': 'kafka3:9092',
            _consumer.Field_Topics: ['events'],
            'service': 'enmasse.kafka.service',
        }

        # The legacy channel comes out with a list
        item = _by_name(exported)[_channel_name_legacy]
        assert item[_consumer.Field_Topics] == ['legacy']
        assert 'topic' not in item

# ################################################################################################################################

    def test_an_outgoing_connection_exports_every_field_moved_away_from_its_default(
        self,
        yaml_config:'stranydict',
        session:'any_',
        outgoing_importer:'OutgoingKafkaImporter',
        outgoing_exporter:'OutgoingKafkaExporter',
    ) -> 'None':
        _, _ = outgoing_importer.sync_definitions(yaml_config['outgoing_kafka'], session)

        exported = outgoing_exporter.export(session, _cluster_id)
        item = _by_name(exported)[_outgoing_name_1]

        assert item['address'] == 'kafka1:9092,kafka2:9092'
        assert item['topic'] == 'outbound'
        assert item[_producer.Field_Compression] == 'zstd'
        assert item[_producer.Field_Acks] == '1'
        assert item[_producer.Field_Is_Idempotent] is False
        assert item[_producer.Field_Max_Message_Size] == 3000000
        assert item[_producer.Field_Linger_Ms] == 25
        assert item[_producer.Field_Send_Timeout] == 15

        assert item[_retry.Field_Max_Retries] == 4
        assert item[_queue.Field_Use_Queue] is True
        assert item[_dlq.Field_Use_DLQ] is False
        assert item[_dlq.Field_Action] == _dlq.Action.Forward
        assert item[_dlq.Field_Retries] == 5
        assert item[_dlq.Field_Retry_Interval] == 300
        assert item[_dlq.Field_Forward_To] == _forward_to
        assert item[_dlq.Field_Keep_Header] is False

        assert item['ssl'] is True
        assert item['ssl_key_file'] == '/etc/kafka/client.key'
        assert KAFKA.Field_SSL_Key_Password not in item
        assert item['security'] == _security_name
        assert item['sasl_mechanism'] == 'PLAIN'

        item = _by_name(exported)[_outgoing_name_2]
        assert item == {
            'name': _outgoing_name_2,
            'address': 'kafka3:9092',
            'topic': 'outbound',
        }

# ################################################################################################################################

    def test_the_export_round_trips_through_the_writer(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelKafkaImporter',
        outgoing_importer:'OutgoingKafkaImporter',
        channel_exporter:'ChannelKafkaExporter',
        outgoing_exporter:'OutgoingKafkaExporter',
        tmp_path:'Path',
    ) -> 'None':
        _, _ = channel_importer.sync_definitions(yaml_config['channel_kafka'], session)
        _, _ = outgoing_importer.sync_definitions(yaml_config['outgoing_kafka'], session)

        exported_channels = channel_exporter.export(session, _cluster_id)
        exported_outgoing = outgoing_exporter.export(session, _cluster_id)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'channel_kafka': exported_channels, 'outgoing_kafka': exported_outgoing})

        written = path.read_text()
        read_back = yaml.safe_load(written)

        assert read_back['channel_kafka'] == exported_channels
        assert read_back['outgoing_kafka'] == exported_outgoing

        # What was exported imports as itself - nothing is created and nothing changes,
        # the importer works on a copy because it rewrites the definitions it is given
        created, updated = channel_importer.sync_definitions(deepcopy(read_back['channel_kafka']), session)
        assert len(created) == 0

        for connection in updated:
            opaque = _opaque(connection)
            item = _by_name(read_back['channel_kafka'])[connection.name]

            if _consumer.Field_Topics in item:
                assert opaque[_consumer.Field_Topics] == '\n'.join(item[_consumer.Field_Topics])

            if _consumer.Field_Routing in item:
                for rule, stored in zip(item[_consumer.Field_Routing], loads(opaque[_consumer.Field_Routing])):
                    for key in _routing.KeyList:
                        assert stored[key] == rule.get(key, '')

        created, _ = outgoing_importer.sync_definitions(deepcopy(read_back['outgoing_kafka']), session)
        assert len(created) == 0

        # A second export is the same as the first
        assert channel_exporter.export(session, _cluster_id) == exported_channels
        assert outgoing_exporter.export(session, _cluster_id) == exported_outgoing

# ################################################################################################################################
# ################################################################################################################################
