# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing SOAP connection's alerts mapping - the same one an outgoing REST connection carries, imported into
# the alert_ opaque keys of the rest type next to the SOAP action and version, the settings left out taking the
# defaults, the status codes travelling as the text they are typed as and a bad one refused, a re-import changing
# nothing, an update making the file the source of truth, and the export writing only what moved away from the
# defaults, last among the connection's fields.

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
from zato.cli.enmasse.exporters.outgoing_soap import OutgoingSOAPExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.outgoing_soap import OutgoingSOAPImporter
from zato.cli.enmasse.util import FileWriter
from zato.common.alerting.object_config import Alerts_Key, storage_name
from zato.common.api import EMAIL, GENERIC
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

# The cluster every object in the test database belongs to
_cluster_id = 1

# The email and LLM connections the alerts mappings name
_smtp_name = 'enmasse.alerts.soap.smtp'
_llm_name = 'enmasse.alerts.soap.llm'

# The connections of the file - one moving a few settings away from their defaults, one carrying no mapping
_conn_name_1 = 'enmasse.alerts.soap.conn.1'
_conn_name_2 = 'enmasse.alerts.soap.conn.2'

# The codes the first connection alerts on, its own rather than the default
_own_status_codes = '401, 403, 4xx'

# The SOAP fault codes the first connection alerts on, its own rather than the default
_own_fault_codes = 'Receiver, x:Timeout'
_default_fault_codes = 'Receiver, Server, Sender, Client'

# The action the first connection calls and the version it speaks
_soap_action = 'urn:crm:orders'
_soap_version = '1.2'

_yaml_text = f"""
outgoing_soap:
  - name: {_conn_name_1}
    host: https://crm.example.com
    url_path: /soap/orders
    soap_action: {_soap_action}
    soap_version: '{_soap_version}'
    alerts:
      status_codes: '{_own_status_codes}'
      status_code_threshold: 5
      fault_codes: '{_own_fault_codes}'
      fault_threshold: 5
      connection_failures: 2
      max_latency: 2500
      email_connection: smtp:{_smtp_name}
      llm_connection: {_llm_name}

  - name: {_conn_name_2}
    host: https://billing.example.com
    url_path: /soap/invoices
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

    smtp = SMTP()
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

    llm = GenericConn()
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
def soap_importer() -> 'OutgoingSOAPImporter':
    out = OutgoingSOAPImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

@pytest.fixture
def soap_exporter() -> 'OutgoingSOAPExporter':
    out = OutgoingSOAPExporter(EnmasseYAMLExporter())
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

class TestOutgoingSOAPAlertsImport:

    def test_a_connection_stores_every_alert_setting_under_its_prefix(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'OutgoingSOAPImporter',
    ) -> 'None':
        created, _ = soap_importer.sync_outgoing_soap(yaml_config['outgoing_soap'], session)
        connection = _by_name(created)[_conn_name_1]

        opaque = _opaque(connection)

        # The codes are stored as the text they were typed as
        assert opaque[storage_name('status_codes')] == _own_status_codes
        assert opaque[storage_name('status_code_threshold')] == 5
        assert opaque[storage_name('fault_codes')] == _own_fault_codes
        assert opaque[storage_name('fault_threshold')] == 5
        assert opaque[storage_name('connection_failures')] == 2
        assert opaque[storage_name('max_latency')] == 2500
        assert opaque[storage_name('email_connection')] == f'smtp:{_smtp_name}'
        assert opaque[storage_name('llm_connection')] == _llm_name

        # What the mapping left out is at its default
        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('consecutive_failures')] == 3
        assert opaque[storage_name('status_codes_window')] == 300
        assert opaque[storage_name('faults_window')] == 300
        assert opaque[storage_name('connection_failures_window')] == 300
        assert opaque[storage_name('latency_window')] == 300
        assert opaque[storage_name('use_llm')] is True

        # A channel's settings never land on a connection
        assert storage_name('auth_failures') not in opaque
        assert storage_name('silence_slots') not in opaque

        # The connection's own attributes are untouched and the mapping itself is not stored
        assert opaque['is_audit_log_active'] is True
        assert connection.host == 'https://crm.example.com'
        assert connection.soap_action == _soap_action
        assert connection.soap_version == _soap_version
        assert Alerts_Key not in opaque
        assert not hasattr(connection, Alerts_Key)

# ################################################################################################################################

    def test_a_connection_without_the_mapping_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'OutgoingSOAPImporter',
    ) -> 'None':
        created, _ = soap_importer.sync_outgoing_soap(yaml_config['outgoing_soap'], session)
        connection = _by_name(created)[_conn_name_2]

        opaque = _opaque(connection)

        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('status_codes')] == '401, 403, 5xx'
        assert opaque[storage_name('status_code_threshold')] == 3
        assert opaque[storage_name('fault_codes')] == _default_fault_codes
        assert opaque[storage_name('fault_threshold')] == 3
        assert opaque[storage_name('faults_window')] == 300
        assert opaque[storage_name('connection_failures')] == 3
        assert opaque[storage_name('max_latency')] == 5000
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

        assert opaque['is_audit_log_active'] is False

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'OutgoingSOAPImporter',
    ) -> 'None':
        created, _ = soap_importer.sync_outgoing_soap(yaml_config['outgoing_soap'], session)
        assert len(created) == 2

        # The same file again changes nothing ..
        definitions = yaml.safe_load(_yaml_text)['outgoing_soap']
        created_again, updated = soap_importer.sync_outgoing_soap(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 0

        # .. and one with a smaller mapping updates the connection it belongs to.
        definitions = yaml.safe_load(_yaml_text)['outgoing_soap']
        definitions[0]['alerts'] = {'connection_failures': 2}

        created_again, updated = soap_importer.sync_outgoing_soap(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 1

        connection = _by_name(updated)[_conn_name_1]
        opaque = _opaque(connection)

        assert opaque[storage_name('connection_failures')] == 2
        assert opaque[storage_name('status_codes')] == '401, 403, 5xx'
        assert opaque[storage_name('status_code_threshold')] == 3
        assert opaque[storage_name('fault_codes')] == _default_fault_codes
        assert opaque[storage_name('fault_threshold')] == 3
        assert opaque[storage_name('max_latency')] == 5000
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

# ################################################################################################################################

    def test_a_bad_status_code_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'OutgoingSOAPImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_soap']
        definitions[0]['alerts']['status_codes'] = '401, 6xx'

        with pytest.raises(Exception) as context:
            _ = soap_importer.sync_outgoing_soap(definitions, session)

        message = str(context.value)
        assert '6xx' in message
        assert 'outgoing SOAP' in message
        assert _conn_name_1 in message

        # Nothing was written
        stored = session.query(HTTPSOAP).filter_by(name=_conn_name_1).first()
        assert stored is None

# ################################################################################################################################

    def test_a_bad_fault_code_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'OutgoingSOAPImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_soap']
        definitions[0]['alerts']['fault_codes'] = 'Receiver, not a code'

        with pytest.raises(Exception) as context:
            _ = soap_importer.sync_outgoing_soap(definitions, session)

        message = str(context.value)
        assert 'not a code' in message
        assert 'outgoing SOAP' in message
        assert _conn_name_1 in message

        # Nothing was written
        stored = session.query(HTTPSOAP).filter_by(name=_conn_name_1).first()
        assert stored is None

# ################################################################################################################################

    def test_a_channel_setting_is_rejected_on_a_connection(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'OutgoingSOAPImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_soap']
        definitions[0]['alerts']['auth_failures'] = 3

        with pytest.raises(Exception) as context:
            _ = soap_importer.sync_outgoing_soap(definitions, session)

        message = str(context.value)
        assert 'auth_failures' in message
        assert _conn_name_1 in message

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingSOAPAlertsExport:

    def test_only_the_settings_moved_away_from_their_defaults_are_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'OutgoingSOAPImporter',
        soap_exporter:'OutgoingSOAPExporter',
    ) -> 'None':
        _, _ = soap_importer.sync_outgoing_soap(yaml_config['outgoing_soap'], session)

        exported = soap_exporter.export(session, _cluster_id)
        item = _by_name(exported)[_conn_name_1]

        expected = {
            'status_codes': _own_status_codes,
            'status_code_threshold': 5,
            'fault_codes': _own_fault_codes,
            'fault_threshold': 5,
            'connection_failures': 2,
            'max_latency': 2500,
            'email_connection': f'smtp:{_smtp_name}',
            'llm_connection': _llm_name,
        }

        assert item[Alerts_Key] == expected
        assert list(item[Alerts_Key]) == list(expected)

        # The SOAP details travel next to the mapping, and the mapping is the last of the fields
        assert item['soap_action'] == _soap_action
        assert item['soap_version'] == _soap_version
        assert list(item)[-1] == Alerts_Key

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
        soap_importer:'OutgoingSOAPImporter',
        soap_exporter:'OutgoingSOAPExporter',
        tmp_path:'Path',
    ) -> 'None':
        _, _ = soap_importer.sync_outgoing_soap(yaml_config['outgoing_soap'], session)
        exported = soap_exporter.export(session, _cluster_id)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'outgoing_soap': exported})

        # The alerts mapping is the last field of a written connection, the codes quoted as the text they are
        written = path.read_text()
        assert f"    alerts:\n      status_codes: '{_own_status_codes}'\n      status_code_threshold: 5\n" in written
        assert f"      fault_codes: '{_own_fault_codes}'\n      fault_threshold: 5\n" in written

        read_back = yaml.safe_load(written)
        assert read_back['outgoing_soap'] == exported

        # The same settings again change nothing
        _, updated = soap_importer.sync_outgoing_soap(read_back['outgoing_soap'], session)
        assert len(updated) == 0

# ################################################################################################################################
# ################################################################################################################################
