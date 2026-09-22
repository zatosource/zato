# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing REST connection's alerts mapping - it imports into the alert_ opaque keys of the rest type, the
# settings left out take the defaults, the status codes travel as the text they are typed as and a bad one is
# refused, a re-import changes nothing, an update makes the file the source of truth, and the export writes only
# what moved away from the defaults, last among the connection's fields.

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
from zato.common.alerting.object_config import Alerts_Key, storage_name
from zato.common.api import EMAIL, GENERIC
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, HTTPSOAP, SecurityBase, Service, SMTP
from zato.common.typing_ import cast_

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

# The cluster every object in the test database belongs to
_cluster_id = 1

# The email and LLM connections the alerts mappings name
_smtp_name = 'enmasse.alerts.rest.smtp'
_llm_name = 'enmasse.alerts.rest.llm'

# The connections of the file - one moving a few settings away from their defaults, one carrying no mapping
_conn_name_1 = 'enmasse.alerts.rest.conn.1'
_conn_name_2 = 'enmasse.alerts.rest.conn.2'

# The codes the first connection alerts on, its own rather than the default
_own_status_codes = '401, 403, 4xx'

_yaml_text = f"""
outgoing_rest:
  - name: {_conn_name_1}
    host: https://crm.example.com
    url_path: /api/v2/customers
    alerts:
      status_codes: '{_own_status_codes}'
      status_code_threshold: 5
      connection_failures: 2
      max_latency: 2500
      dlq_messages: 2
      queue_depth: 500
      email_connection: smtp:{_smtp_name}
      llm_connection: {_llm_name}

  - name: {_conn_name_2}
    host: https://billing.example.com
    url_path: /api/invoices
    is_audit_log_active: false
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
    """ A real ODB session over an in-memory SQLite database holding one cluster and the SMTP and LLM
    connections the alerts mappings name.
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

    smtp = cast_('any_', SMTP())
    smtp.name = _smtp_name
    smtp.is_active = True
    smtp.host = 'smtp.example.com'
    smtp.port = 587
    smtp.timeout = 30
    smtp.is_debug = False
    smtp.mode = EMAIL.SMTP.MODE.STARTTLS
    smtp.ping_address = 'ping@example.com'
    smtp.cluster = cluster
    session.add(smtp)

    llm = cast_('any_', GenericConn())
    llm.name = _llm_name
    llm.type_ = GENERIC.CONNECTION.TYPE.OUTCONN_LLM
    llm.is_active = True
    llm.is_internal = False
    llm.is_channel = False
    llm.is_outconn = True
    llm.cluster = cluster
    session.add(llm)

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
# ################################################################################################################################

class TestOutgoingRESTAlertsImport:

    def test_a_connection_stores_every_alert_setting_under_its_prefix(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        created, _ = rest_importer.sync_outgoing_rest(yaml_config['outgoing_rest'], session)
        connection = _by_name(created)[_conn_name_1]

        opaque = _opaque(connection)

        # The codes are stored as the text they were typed as
        assert opaque[storage_name('status_codes')] == _own_status_codes
        assert opaque[storage_name('status_code_threshold')] == 5
        assert opaque[storage_name('connection_failures')] == 2
        assert opaque[storage_name('max_latency')] == 2500
        assert opaque[storage_name('dlq_messages')] == 2
        assert opaque[storage_name('queue_depth')] == 500
        assert opaque[storage_name('email_connection')] == f'smtp:{_smtp_name}'
        assert opaque[storage_name('llm_connection')] == _llm_name

        # What the mapping left out is at its default
        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('consecutive_failures')] == 3
        assert opaque[storage_name('status_codes_window')] == 300
        assert opaque[storage_name('connection_failures_window')] == 300
        assert opaque[storage_name('latency_window')] == 300
        assert opaque[storage_name('use_llm')] is True

        # A channel's settings never land on a connection
        assert storage_name('auth_failures') not in opaque
        assert storage_name('silence_slots') not in opaque

        # The connection's own attributes are untouched and the mapping itself is not stored
        assert opaque['is_audit_log_active'] is True
        assert connection.host == 'https://crm.example.com'
        assert Alerts_Key not in opaque
        assert not hasattr(connection, Alerts_Key)

# ################################################################################################################################

    def test_a_connection_without_the_mapping_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        created, _ = rest_importer.sync_outgoing_rest(yaml_config['outgoing_rest'], session)
        connection = _by_name(created)[_conn_name_2]

        opaque = _opaque(connection)

        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('status_codes')] == '401, 403, 5xx'
        assert opaque[storage_name('status_code_threshold')] == 3
        assert opaque[storage_name('connection_failures')] == 3
        assert opaque[storage_name('max_latency')] == 5000
        assert opaque[storage_name('dlq_messages')] == 1
        assert opaque[storage_name('queue_depth')] == 1000
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

        assert opaque['is_audit_log_active'] is False

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        created, _ = rest_importer.sync_outgoing_rest(yaml_config['outgoing_rest'], session)
        assert len(created) == 2

        # The same file again changes nothing ..
        definitions = yaml.safe_load(_yaml_text)['outgoing_rest']
        created_again, updated = rest_importer.sync_outgoing_rest(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 0

        # .. and one with a smaller mapping updates the connection it belongs to.
        definitions = yaml.safe_load(_yaml_text)['outgoing_rest']
        definitions[0]['alerts'] = {'connection_failures': 2}

        created_again, updated = rest_importer.sync_outgoing_rest(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 1

        connection = _by_name(updated)[_conn_name_1]
        opaque = _opaque(connection)

        assert opaque[storage_name('connection_failures')] == 2
        assert opaque[storage_name('status_codes')] == '401, 403, 5xx'
        assert opaque[storage_name('status_code_threshold')] == 3
        assert opaque[storage_name('max_latency')] == 5000
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

# ################################################################################################################################

    def test_a_bad_status_code_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_rest']
        definitions[0]['alerts']['status_codes'] = '401, 6xx'

        with pytest.raises(Exception) as context:
            _ = rest_importer.sync_outgoing_rest(definitions, session)

        message = str(context.value)
        assert '6xx' in message
        assert 'outgoing REST' in message
        assert _conn_name_1 in message

        # Nothing was written
        stored = session.query(HTTPSOAP).filter_by(name=_conn_name_1).first()
        assert stored is None

# ################################################################################################################################

    def test_a_channel_setting_is_rejected_on_a_connection(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'OutgoingRESTImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_rest']
        definitions[0]['alerts']['auth_failures'] = 3

        with pytest.raises(Exception) as context:
            _ = rest_importer.sync_outgoing_rest(definitions, session)

        message = str(context.value)
        assert 'auth_failures' in message
        assert _conn_name_1 in message

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingRESTAlertsExport:

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

        expected = {
            'status_codes': _own_status_codes,
            'status_code_threshold': 5,
            'connection_failures': 2,
            'max_latency': 2500,
            'dlq_messages': 2,
            'queue_depth': 500,
            'email_connection': f'smtp:{_smtp_name}',
            'llm_connection': _llm_name,
        }

        assert item[Alerts_Key] == expected
        assert list(item[Alerts_Key]) == list(expected)

        for key in item:
            assert not key.startswith('alert_')

        # A connection that moved nothing carries no alerts key
        item = _by_name(exported)[_conn_name_2]
        assert Alerts_Key not in item
        assert item['is_audit_log_active'] is False

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

        # The alerts mapping is the last field of a written connection, the codes quoted as the text they are
        written = path.read_text()
        assert f"    alerts:\n      status_codes: '{_own_status_codes}'\n      status_code_threshold: 5\n" in written

        read_back = yaml.safe_load(written)
        assert read_back['outgoing_rest'] == exported

        # The same settings again change nothing
        _, updated = rest_importer.sync_outgoing_rest(read_back['outgoing_rest'], session)
        assert len(updated) == 0

# ################################################################################################################################
# ################################################################################################################################
