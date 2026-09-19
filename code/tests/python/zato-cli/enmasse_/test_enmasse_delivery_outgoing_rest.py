# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue switch and the DLQ settings of an outgoing REST connection in enmasse.

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
from zato.cli.enmasse.exporters.outgoing_rest import OutgoingRESTExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
from zato.cli.enmasse.util import FileWriter
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

# One connection moves every delivery setting away from its default, the other carries none of them
_conn_name_1 = 'enmasse.delivery.rest.conn.1'
_conn_name_2 = 'enmasse.delivery.rest.conn.2'

_forward_to = 'enmasse.delivery.rest.topic'

_yaml_text = f"""
outgoing_rest:
  - name: {_conn_name_1}
    host: https://crm.example.com
    url_path: /api/v2/customers
    max_retries: 4
    use_queue: true
    use_dlq: false
    dlq_action: forward
    dlq_retries: 5
    dlq_retry_interval: 300
    dlq_forward_to: {_forward_to}
    dlq_keep_header: false

  - name: {_conn_name_2}
    host: https://billing.example.com
    url_path: /api/invoices
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
    """ A real ODB session over an in-memory SQLite database holding one cluster.
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
    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def rest_importer() -> 'OutgoingRESTImporter':
    out = OutgoingRESTImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

@pytest.fixture
def rest_exporter() -> 'OutgoingRESTExporter':
    out = OutgoingRESTExporter(EnmasseYAMLExporter())
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

def _definitions() -> 'any_':
    out = yaml.safe_load(_yaml_text)['outgoing_rest']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingRESTDeliveryImport:

    def test_a_connection_stores_every_delivery_setting(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        created, _ = rest_importer.sync_outgoing_rest(yaml_config['outgoing_rest'], session)
        connection = _by_name(created)[_conn_name_1]

        opaque = _opaque(connection)

        assert opaque[_queue.Field_Use_Queue] is True
        assert opaque[_dlq.Field_Use_DLQ] is False
        assert opaque[_dlq.Field_Action] == _dlq.Action.Forward
        assert opaque[_dlq.Field_Retries] == 5
        assert opaque[_dlq.Field_Retry_Interval] == 300
        assert opaque[_dlq.Field_Forward_To] == _forward_to
        assert opaque[_dlq.Field_Keep_Header] is False

        assert opaque['max_retries'] == 4

        assert connection.host == 'https://crm.example.com'

# ################################################################################################################################

    def test_a_connection_without_the_settings_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        created, _ = rest_importer.sync_outgoing_rest(yaml_config['outgoing_rest'], session)
        connection = _by_name(created)[_conn_name_2]

        opaque = _opaque(connection)

        assert opaque[_queue.Field_Use_Queue] is False
        assert opaque[_dlq.Field_Use_DLQ] is True
        assert opaque[_dlq.Field_Action] == _dlq.Action.Keep
        assert opaque[_dlq.Field_Retries] == 3
        assert opaque[_dlq.Field_Retry_Interval] == 60
        assert opaque[_dlq.Field_Forward_To] == ''
        assert opaque[_dlq.Field_Keep_Header] is True

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        created, _ = rest_importer.sync_outgoing_rest(yaml_config['outgoing_rest'], session)
        assert len(created) == 2

        created_again, updated = rest_importer.sync_outgoing_rest(_definitions(), session)
        assert len(created_again) == 0
        assert len(updated) == 0

        definitions = _definitions()
        for name in _dlq.FieldList:
            del definitions[0][name]

        created_again, updated = rest_importer.sync_outgoing_rest(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 1

        connection = _by_name(updated)[_conn_name_1]
        opaque = _opaque(connection)

        assert opaque[_queue.Field_Use_Queue] is True
        assert opaque[_dlq.Field_Use_DLQ] is True
        assert opaque[_dlq.Field_Action] == _dlq.Action.Keep
        assert opaque[_dlq.Field_Retries] == 3
        assert opaque[_dlq.Field_Retry_Interval] == 60
        assert opaque[_dlq.Field_Forward_To] == ''
        assert opaque[_dlq.Field_Keep_Header] is True

        definitions[1][_queue.Field_Use_Queue] = True

        created_again, updated = rest_importer.sync_outgoing_rest(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 1

        connection = _by_name(updated)[_conn_name_2]
        assert _opaque(connection)[_queue.Field_Use_Queue] is True

# ################################################################################################################################

    def test_a_forward_without_a_topic_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_rest']
        del definitions[0][_dlq.Field_Forward_To]

        with pytest.raises(Exception) as context:
            _ = rest_importer.sync_outgoing_rest(definitions, session)

        message = str(context.value)
        assert _dlq.Field_Forward_To in message
        assert 'outgoing REST' in message
        assert _conn_name_1 in message

        stored = session.query(HTTPSOAP).filter_by(name=_conn_name_1).first()
        assert stored is None

# ################################################################################################################################

    def test_a_negative_count_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_rest']
        definitions[0][_dlq.Field_Retries] = -1

        with pytest.raises(Exception) as context:
            _ = rest_importer.sync_outgoing_rest(definitions, session)

        message = str(context.value)
        assert _dlq.Field_Retries in message
        assert 'negative' in message
        assert _conn_name_1 in message

# ################################################################################################################################

    def test_a_switch_that_is_not_a_boolean_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_rest']
        definitions[0][_queue.Field_Use_Queue] = 'yes'

        with pytest.raises(Exception) as context:
            _ = rest_importer.sync_outgoing_rest(definitions, session)

        message = str(context.value)
        assert _queue.Field_Use_Queue in message
        assert 'boolean' in message
        assert _conn_name_1 in message

# ################################################################################################################################

    def test_an_unknown_action_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_rest']
        definitions[0][_dlq.Field_Action] = 'archive'

        with pytest.raises(Exception) as context:
            _ = rest_importer.sync_outgoing_rest(definitions, session)

        message = str(context.value)
        assert 'archive' in message
        assert _dlq.Action.Forward in message
        assert _conn_name_1 in message

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingRESTDeliveryExport:

    def test_only_the_settings_moved_away_from_their_defaults_are_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
        rest_exporter:'OutgoingRESTExporter',
    ) -> 'None':
        _, _ = rest_importer.sync_outgoing_rest(yaml_config['outgoing_rest'], session)

        exported = rest_exporter.export(session, _cluster_id)
        item = _by_name(exported)[_conn_name_1]

        assert item[_queue.Field_Use_Queue] is True
        assert item[_dlq.Field_Use_DLQ] is False
        assert item[_dlq.Field_Action] == _dlq.Action.Forward
        assert item[_dlq.Field_Retries] == 5
        assert item[_dlq.Field_Retry_Interval] == 300
        assert item[_dlq.Field_Forward_To] == _forward_to
        assert item[_dlq.Field_Keep_Header] is False

        item = _by_name(exported)[_conn_name_2]

        assert _queue.Field_Use_Queue not in item
        for name in _dlq.FieldList:
            assert name not in item

# ################################################################################################################################

    def test_the_export_round_trips_through_the_writer(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
        rest_exporter:'OutgoingRESTExporter',
        tmp_path:'Path',
    ) -> 'None':
        _, _ = rest_importer.sync_outgoing_rest(yaml_config['outgoing_rest'], session)
        exported = rest_exporter.export(session, _cluster_id)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'outgoing_rest': exported})

        # In field order, right after the retry fields
        written = path.read_text()
        expected = '    max_retries: 4\n' \
            '    use_queue: True\n' \
            '    use_dlq: False\n' \
            '    dlq_action: forward\n' \
            '    dlq_retries: 5\n' \
            '    dlq_retry_interval: 300\n' \
            f'    dlq_forward_to: {_forward_to}\n' \
            '    dlq_keep_header: False\n'
        assert expected in written, written

        read_back = yaml.safe_load(written)
        assert read_back['outgoing_rest'] == exported

        _, updated = rest_importer.sync_outgoing_rest(read_back['outgoing_rest'], session)
        assert len(updated) == 0

# ################################################################################################################################
# ################################################################################################################################
