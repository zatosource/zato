# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue switch, the DLQ settings and the static queue response of a REST channel in enmasse.

# stdlib
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
from zato.cli.enmasse.exporters.channel_rest import ChannelExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.cli.enmasse.util import channel_delivery_needs_update, FileWriter
from zato.common.api import HTTP_SOAP
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, HTTPSOAP, SecurityBase, Service, SMTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_
    anydict = anydict
    Path = Path
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ

_cluster_id = 1

# The service every channel of the file invokes
_service_name = 'enmasse.delivery.channel.rest.service'

# The first channel moves every delivery setting away from its default and answers with a JSON document,
# the second carries none of the settings, the third answers with XML and the fourth with plain text spanning two lines
_channel_name_1 = 'enmasse.delivery.channel.rest.1'
_channel_name_2 = 'enmasse.delivery.channel.rest.2'
_channel_name_3 = 'enmasse.delivery.channel.rest.3'
_channel_name_4 = 'enmasse.delivery.channel.rest.4'

_forward_to = 'enmasse.delivery.channel.rest.topic'

_queue_response_json = '{"accepted": true, "queue": "orders"}'
_queue_response_xml = '<ack><accepted>true</accepted></ack>'
_queue_response_text = 'ACCEPTED\nThank you for your order'

_yaml_text = f"""
channel_rest:
  - name: {_channel_name_1}
    service: {_service_name}
    url_path: /enmasse/delivery/channel/rest/1
    max_retries: 4
    use_queue: true
    use_dlq: false
    dlq_action: forward
    dlq_retries: 5
    dlq_retry_interval: 300
    dlq_forward_to: {_forward_to}
    dlq_keep_header: false
    queue_response: '{_queue_response_json}'

  - name: {_channel_name_2}
    service: {_service_name}
    url_path: /enmasse/delivery/channel/rest/2

  - name: {_channel_name_3}
    service: {_service_name}
    url_path: /enmasse/delivery/channel/rest/3
    use_queue: true
    queue_response: '{_queue_response_xml}'

  - name: {_channel_name_4}
    service: {_service_name}
    url_path: /enmasse/delivery/channel/rest/4
    use_queue: true
    queue_response: |-
      ACCEPTED
      Thank you for your order
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
    """ A real ODB session over an in-memory SQLite database holding one cluster and the service the channels invoke.
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
        HTTPSOAP.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

    service = Service(None, _service_name, True, 'enmasse.delivery.channel.rest.Service', False, cluster)
    session.add(service)

    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def channel_importer() -> 'ChannelImporter':
    out = ChannelImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

@pytest.fixture
def channel_exporter() -> 'ChannelExporter':
    out = ChannelExporter(EnmasseYAMLExporter())
    return out

# ################################################################################################################################

def _opaque(channel:'any_') -> 'anydict':
    out = loads(channel.opaque1)
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

def _definitions() -> 'any_':
    out = yaml.safe_load(_yaml_text)['channel_rest']
    return out

# ################################################################################################################################

def _trimmed_definitions() -> 'any_':
    """ The definitions with the retry config, the DLQ settings and the static response gone from the first channel.
    """
    out = _definitions()

    for name in _dlq.FieldList:
        del out[0][name]

    del out[0][_queue.Field_Queue_Response]
    del out[0]['max_retries']

    return out

# ################################################################################################################################

def _db_defs(channel_importer:'ChannelImporter', session:'any_') -> 'anydict':
    out = channel_importer.get_rest_channels_from_db(session, _cluster_id)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelDeliveryImport:

    def test_a_channel_stores_every_delivery_setting(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        created, _ = channel_importer.sync_channel_rest(yaml_config['channel_rest'], session)
        channel = _by_name(created)[_channel_name_1]

        opaque = _opaque(channel)

        assert opaque[_queue.Field_Use_Queue] is True
        assert opaque[_dlq.Field_Use_DLQ] is False
        assert opaque[_dlq.Field_Action] == _dlq.Action.Forward
        assert opaque[_dlq.Field_Retries] == 5
        assert opaque[_dlq.Field_Retry_Interval] == 300
        assert opaque[_dlq.Field_Forward_To] == _forward_to
        assert opaque[_dlq.Field_Keep_Header] is False
        assert opaque[_queue.Field_Queue_Response] == _queue_response_json

        assert opaque['max_retries'] == 4

        assert channel.url_path == '/enmasse/delivery/channel/rest/1'

# ################################################################################################################################

    def test_a_channel_without_the_settings_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        created, _ = channel_importer.sync_channel_rest(yaml_config['channel_rest'], session)
        channel = _by_name(created)[_channel_name_2]

        opaque = _opaque(channel)

        assert opaque[_queue.Field_Use_Queue] is False
        assert opaque[_dlq.Field_Use_DLQ] is True
        assert opaque[_dlq.Field_Action] == _dlq.Action.Keep
        assert opaque[_dlq.Field_Retries] == 3
        assert opaque[_dlq.Field_Retry_Interval] == 60
        assert opaque[_dlq.Field_Forward_To] == ''
        assert opaque[_dlq.Field_Keep_Header] is True
        assert opaque[_queue.Field_Queue_Response] == ''

        assert opaque['max_retries'] == 0

# ################################################################################################################################

    def test_the_static_response_keeps_its_exact_text(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        created, _ = channel_importer.sync_channel_rest(yaml_config['channel_rest'], session)
        channels = _by_name(created)

        assert _opaque(channels[_channel_name_3])[_queue.Field_Queue_Response] == _queue_response_xml
        assert _opaque(channels[_channel_name_4])[_queue.Field_Queue_Response] == _queue_response_text

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        created, _ = channel_importer.sync_channel_rest(yaml_config['channel_rest'], session)
        assert len(created) == 4

        created_again, updated = channel_importer.sync_channel_rest(_definitions(), session)
        assert len(created_again) == 0
        assert len(updated) == 0

        # The retry config, the DLQ settings and the static response leave the first channel
        created_again, updated = channel_importer.sync_channel_rest(_trimmed_definitions(), session)
        assert len(created_again) == 0
        assert len(updated) == 1

        channel = _by_name(updated)[_channel_name_1]
        opaque = _opaque(channel)

        assert opaque[_queue.Field_Use_Queue] is True
        assert opaque[_dlq.Field_Use_DLQ] is True
        assert opaque[_dlq.Field_Action] == _dlq.Action.Keep
        assert opaque[_dlq.Field_Retries] == 3
        assert opaque[_dlq.Field_Retry_Interval] == 60
        assert opaque[_dlq.Field_Forward_To] == ''
        assert opaque[_dlq.Field_Keep_Header] is True
        assert opaque[_queue.Field_Queue_Response] == ''
        assert opaque['max_retries'] == 0

        # The queue switch arrives on the second channel - the importer takes the delivery keys out of the definitions
        # it is given, so each import works on definitions of its own
        definitions = _trimmed_definitions()
        definitions[1][_queue.Field_Use_Queue] = True

        created_again, updated = channel_importer.sync_channel_rest(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 1

        channel = _by_name(updated)[_channel_name_2]
        assert _opaque(channel)[_queue.Field_Use_Queue] is True

# ################################################################################################################################

    def test_a_static_response_without_the_queue_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        definitions = yaml_config['channel_rest']
        definitions[2][_queue.Field_Use_Queue] = False

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_channel_rest(definitions, session)

        message = str(context.value)
        assert _queue.Field_Queue_Response in message
        assert _queue.Field_Use_Queue in message
        assert _channel_name_3 in message

        stored = session.query(HTTPSOAP).filter_by(name=_channel_name_3).first()
        assert stored is None

# ################################################################################################################################

    def test_a_static_response_that_is_not_a_string_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        definitions = yaml_config['channel_rest']
        definitions[2][_queue.Field_Queue_Response] = {'accepted': True}

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_channel_rest(definitions, session)

        message = str(context.value)
        assert _queue.Field_Queue_Response in message
        assert 'string' in message
        assert _channel_name_3 in message

# ################################################################################################################################

    def test_a_forward_without_a_topic_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        definitions = yaml_config['channel_rest']
        del definitions[0][_dlq.Field_Forward_To]

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_channel_rest(definitions, session)

        message = str(context.value)
        assert _dlq.Field_Forward_To in message
        assert _channel_name_1 in message

        stored = session.query(HTTPSOAP).filter_by(name=_channel_name_1).first()
        assert stored is None

# ################################################################################################################################

    def test_a_negative_count_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        definitions = yaml_config['channel_rest']
        definitions[0][_dlq.Field_Retries] = -1

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_channel_rest(definitions, session)

        message = str(context.value)
        assert _dlq.Field_Retries in message
        assert 'negative' in message
        assert _channel_name_1 in message

# ################################################################################################################################

    def test_a_switch_that_is_not_a_boolean_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        definitions = yaml_config['channel_rest']
        definitions[0][_queue.Field_Use_Queue] = 'yes'

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_channel_rest(definitions, session)

        message = str(context.value)
        assert _queue.Field_Use_Queue in message
        assert 'boolean' in message
        assert _channel_name_1 in message

# ################################################################################################################################

    def test_an_unknown_action_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        definitions = yaml_config['channel_rest']
        definitions[0][_dlq.Field_Action] = 'archive'

        with pytest.raises(Exception) as context:
            _ = channel_importer.sync_channel_rest(definitions, session)

        message = str(context.value)
        assert 'archive' in message
        assert _dlq.Action.Forward in message
        assert _channel_name_1 in message

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelDeliveryCompare:

    def test_a_second_import_of_the_same_file_changes_nothing(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        _, _ = channel_importer.sync_channel_rest(yaml_config['channel_rest'], session)

        db_defs = _db_defs(channel_importer, session)

        for definition in _definitions():
            assert not channel_delivery_needs_update(definition, db_defs[definition['name']]), definition['name']

# ################################################################################################################################

    def test_each_delivery_key_is_compared(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        _, _ = channel_importer.sync_channel_rest(yaml_config['channel_rest'], session)

        db_defs = _db_defs(channel_importer, session)
        db_def = db_defs[_channel_name_1]

        changes = {
            'max_retries': 9,
            _queue.Field_Use_Queue: False,
            _dlq.Field_Use_DLQ: True,
            _dlq.Field_Action: _dlq.Action.Discard,
            _dlq.Field_Retries: 1,
            _dlq.Field_Retry_Interval: 1,
            _dlq.Field_Forward_To: 'another.topic',
            _dlq.Field_Keep_Header: True,
            _queue.Field_Queue_Response: '{"accepted": false}',
        }

        for name, value in changes.items():
            definition = _definitions()[0]
            definition[name] = value
            assert channel_delivery_needs_update(definition, db_def), name

# ################################################################################################################################

    def test_a_cleared_static_response_is_a_change(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
    ) -> 'None':
        _, _ = channel_importer.sync_channel_rest(yaml_config['channel_rest'], session)

        db_def = _db_defs(channel_importer, session)[_channel_name_1]

        definition = _definitions()[0]
        del definition[_queue.Field_Queue_Response]

        assert channel_delivery_needs_update(definition, db_def)

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelDeliveryExport:

    def test_only_the_settings_moved_away_from_their_defaults_are_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
        channel_exporter:'ChannelExporter',
    ) -> 'None':
        _, _ = channel_importer.sync_channel_rest(yaml_config['channel_rest'], session)

        exported = channel_exporter.export(session, _cluster_id)
        item = _by_name(exported)[_channel_name_1]

        assert item['max_retries'] == 4
        assert item[_queue.Field_Use_Queue] is True
        assert item[_dlq.Field_Use_DLQ] is False
        assert item[_dlq.Field_Action] == _dlq.Action.Forward
        assert item[_dlq.Field_Retries] == 5
        assert item[_dlq.Field_Retry_Interval] == 300
        assert item[_dlq.Field_Forward_To] == _forward_to
        assert item[_dlq.Field_Keep_Header] is False
        assert item[_queue.Field_Queue_Response] == _queue_response_json

        item = _by_name(exported)[_channel_name_2]

        assert 'max_retries' not in item
        assert _queue.Field_Use_Queue not in item
        assert _queue.Field_Queue_Response not in item
        for name in _dlq.FieldList:
            assert name not in item

# ################################################################################################################################

    def test_the_static_response_is_written_only_when_not_empty(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
        channel_exporter:'ChannelExporter',
    ) -> 'None':
        definitions = yaml_config['channel_rest']
        definitions[2][_queue.Field_Queue_Response] = ''

        _, _ = channel_importer.sync_channel_rest(definitions, session)

        exported = _by_name(channel_exporter.export(session, _cluster_id))

        assert _queue.Field_Queue_Response not in exported[_channel_name_3]
        assert exported[_channel_name_3][_queue.Field_Use_Queue] is True

# ################################################################################################################################

    def test_the_export_round_trips_through_the_writer(
        self,
        yaml_config:'stranydict',
        session:'any_',
        channel_importer:'ChannelImporter',
        channel_exporter:'ChannelExporter',
        tmp_path:'Path',
    ) -> 'None':
        _, _ = channel_importer.sync_channel_rest(yaml_config['channel_rest'], session)
        exported = channel_exporter.export(session, _cluster_id)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'channel_rest': exported})

        # In field order - the retry config, then the queue switch and the DLQ settings, then the static response
        written = path.read_text()
        expected_lines = [
            '    max_retries: 4',
            '    use_queue: True',
            '    use_dlq: False',
            '    dlq_action: forward',
            '    dlq_retries: 5',
            '    dlq_retry_interval: 300',
            f'    dlq_forward_to: {_forward_to}',
            '    dlq_keep_header: False',
            '    queue_response: ',
        ]
        expected = '\n'.join(expected_lines)
        assert expected in written, written

        # Each static response comes back as the exact text it was
        read_back = yaml.safe_load(written)
        assert read_back['channel_rest'] == exported

        items = _by_name(read_back['channel_rest'])
        assert items[_channel_name_1][_queue.Field_Queue_Response] == _queue_response_json
        assert items[_channel_name_3][_queue.Field_Queue_Response] == _queue_response_xml
        assert items[_channel_name_4][_queue.Field_Queue_Response] == _queue_response_text

        _, updated = channel_importer.sync_channel_rest(read_back['channel_rest'], session)
        assert len(updated) == 0

# ################################################################################################################################
# ################################################################################################################################
