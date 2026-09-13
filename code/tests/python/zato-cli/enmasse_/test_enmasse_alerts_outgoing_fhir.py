# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing FHIR connection's alerts mapping - the REST settings plus the outcome codes, imported into the alert_
# opaque keys of the fhir type next to the connection's own fields, the settings left out taking the defaults, the codes
# travelling as the text they are typed as and a bad one refused, a health check creating its scheduler job and travelling
# as how often it runs, a re-import of the same file storing the same settings, an update making the file the source of
# truth, and the export writing only what moved away from the defaults, last among the connection's fields.

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
from zato.cli.enmasse.exporters.outgoing_fhir import OutgoingFHIRExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.outgoing_fhir import OutgoingFHIRImporter
from zato.cli.enmasse.util import FileWriter
from zato.common.alerting.object_config import Alerts_Key, storage_name
from zato.common.api import EMAIL, GENERIC, HTTP_SOAP, SchedulerLink
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, IntervalBasedJob, Job, \
    SecurityBase, Service, SMTP

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

_health_check = HTTP_SOAP.HealthCheck
_fhir_type = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR

# The cluster every object in the test database belongs to
_cluster_id = 1

# The email and LLM connections the alerts mappings name
_smtp_name = 'enmasse.alerts.fhir.smtp'
_llm_name = 'enmasse.alerts.fhir.llm'

# The connections of the file - one moving a few settings away from their defaults, one carrying no mapping
_conn_name_1 = 'enmasse.alerts.fhir.conn.1'
_conn_name_2 = 'enmasse.alerts.fhir.conn.2'

_address_1 = 'https://ehr.example.com/fhir/r4'
_address_2 = 'https://lab.example.com/fhir/r4'

# The codes the first connection alerts on, its own rather than the default
_own_status_codes = '401, 403, 4xx'
_own_outcome_codes = 'exception, not-found'
_default_outcome_codes = 'exception, transient, timeout, throttled, lock-error, no-store, too-costly'

# How often the first connection's health check pings
_run_every = 5
_run_unit = 'minutes'

_yaml_text = f"""
outgoing_fhir:
  - name: {_conn_name_1}
    address: {_address_1}
    health_check_run_every: {_run_every}
    health_check_run_unit: {_run_unit}
    alerts:
      status_codes: '{_own_status_codes}'
      status_code_threshold: 5
      outcome_codes: '{_own_outcome_codes}'
      outcome_threshold: 5
      connection_failures: 2
      max_latency: 2500
      email_connection: smtp:{_smtp_name}
      llm_connection: {_llm_name}

  - name: {_conn_name_2}
    address: {_address_2}
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
    """ A real ODB session over an in-memory SQLite database holding one cluster, the SMTP and LLM connections
    the alerts mappings name and the service a health check job invokes.
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
        Job.__table__,
        IntervalBasedJob.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

    session.add(Service(None, _health_check.Dispatch_Service, True, 'zato.server.service.internal.connection.HealthCheckRun',
        True, cluster))

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
def fhir_importer() -> 'OutgoingFHIRImporter':
    out = OutgoingFHIRImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

@pytest.fixture
def fhir_exporter() -> 'OutgoingFHIRExporter':
    out = OutgoingFHIRExporter(EnmasseYAMLExporter())
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

def _stored(session:'any_', name:'str') -> 'any_':
    out = session.query(GenericConn).filter_by(type_=_fhir_type, name=name).first()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingFHIRAlertsImport:

    def test_a_connection_stores_every_alert_setting_under_its_prefix(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        created, _ = fhir_importer.sync_definitions(yaml_config['outgoing_fhir'], session)
        connection = _by_name(created)[_conn_name_1]

        opaque = _opaque(connection)

        # The codes are stored as the text they were typed as
        assert opaque[storage_name('status_codes')] == _own_status_codes
        assert opaque[storage_name('status_code_threshold')] == 5
        assert opaque[storage_name('outcome_codes')] == _own_outcome_codes
        assert opaque[storage_name('outcome_threshold')] == 5
        assert opaque[storage_name('connection_failures')] == 2
        assert opaque[storage_name('max_latency')] == 2500
        assert opaque[storage_name('email_connection')] == f'smtp:{_smtp_name}'
        assert opaque[storage_name('llm_connection')] == _llm_name

        # What the mapping left out is at its default
        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('consecutive_failures')] == 3
        assert opaque[storage_name('status_codes_window')] == 300
        assert opaque[storage_name('outcomes_window')] == 300
        assert opaque[storage_name('connection_failures_window')] == 300
        assert opaque[storage_name('latency_window')] == 300
        assert opaque[storage_name('use_llm')] is True

        # Neither a channel's settings nor a SOAP connection's faults ever land on a FHIR connection
        assert storage_name('auth_failures') not in opaque
        assert storage_name('silence_slots') not in opaque
        assert storage_name('fault_codes') not in opaque

        # The connection's own attributes are untouched and the mapping itself is not stored
        assert opaque['is_audit_log_active'] is True
        assert connection.address == _address_1
        assert connection.type_ == _fhir_type
        assert Alerts_Key not in opaque
        assert not hasattr(connection, Alerts_Key)

# ################################################################################################################################

    def test_a_connection_without_the_mapping_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        created, _ = fhir_importer.sync_definitions(yaml_config['outgoing_fhir'], session)
        connection = _by_name(created)[_conn_name_2]

        opaque = _opaque(connection)

        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('status_codes')] == '401, 403, 5xx'
        assert opaque[storage_name('status_code_threshold')] == 3
        assert opaque[storage_name('outcome_codes')] == _default_outcome_codes
        assert opaque[storage_name('outcome_threshold')] == 3
        assert opaque[storage_name('outcomes_window')] == 300
        assert opaque[storage_name('connection_failures')] == 3
        assert opaque[storage_name('max_latency')] == 5000
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

        assert opaque['is_audit_log_active'] is False

        # No health check was asked for, so none is stored and no job exists for it
        assert _health_check.Field_Run_Every not in opaque
        assert _health_check.Field_Job_ID not in opaque
        assert session.query(Job).filter_by(name=_health_check.Job_Prefix + _conn_name_2).first() is None

# ################################################################################################################################

    def test_a_health_check_creates_its_job_as_a_fhir_one(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        created, _ = fhir_importer.sync_definitions(yaml_config['outgoing_fhir'], session)
        connection = _by_name(created)[_conn_name_1]

        # The job exists, named after the connection, invoking the health check service on the schedule asked for ..
        job = session.query(Job).filter_by(name=_health_check.Job_Prefix + _conn_name_1).one()
        assert job.service.name == _health_check.Dispatch_Service
        assert job.interval_based.minutes == _run_every

        job_opaque = loads(job.opaque1)
        assert job_opaque[SchedulerLink.Conn_Type] == SchedulerLink.ConnType.FHIR_Outgoing
        assert job_opaque[SchedulerLink.Conn_ID] == connection.id
        assert job_opaque[SchedulerLink.Kind] == SchedulerLink.KindType.HealthCheck

        extra = loads(job.extra)
        assert extra == {
            _health_check.Extra_Conn_ID: connection.id,
            _health_check.Extra_Conn_Name: _conn_name_1,
            _health_check.Extra_Conn_Type: SchedulerLink.ConnType.FHIR_Outgoing,
        }

        # .. and the connection remembers the job and how often it runs.
        opaque = _opaque(connection)
        assert opaque[_health_check.Field_Run_Every] == _run_every
        assert opaque[_health_check.Field_Run_Unit] == _run_unit
        assert opaque[_health_check.Field_Job_ID] == job.id

        # The same file again finds the job by its name rather than creating another
        _, _ = fhir_importer.sync_definitions(yaml.safe_load(_yaml_text)['outgoing_fhir'], session)
        assert session.query(Job).filter_by(name=_health_check.Job_Prefix + _conn_name_1).count() == 1

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        created, _ = fhir_importer.sync_definitions(yaml_config['outgoing_fhir'], session)
        assert len(created) == 2

        # The same file again writes the same settings - a generic connection is rewritten from its file on every import ..
        definitions = yaml.safe_load(_yaml_text)['outgoing_fhir']
        created_again, updated = fhir_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 2

        opaque = _opaque(_by_name(updated)[_conn_name_1])
        assert opaque[storage_name('outcome_codes')] == _own_outcome_codes
        assert opaque[storage_name('outcome_threshold')] == 5

        # .. and one with a smaller mapping updates the connection it belongs to.
        definitions = yaml.safe_load(_yaml_text)['outgoing_fhir']
        definitions[0]['alerts'] = {'connection_failures': 2}

        created_again, updated = fhir_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0

        connection = _by_name(updated)[_conn_name_1]
        opaque = _opaque(connection)

        assert opaque[storage_name('connection_failures')] == 2
        assert opaque[storage_name('status_codes')] == '401, 403, 5xx'
        assert opaque[storage_name('status_code_threshold')] == 3
        assert opaque[storage_name('outcome_codes')] == _default_outcome_codes
        assert opaque[storage_name('outcome_threshold')] == 3
        assert opaque[storage_name('max_latency')] == 5000
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

# ################################################################################################################################

    def test_a_bad_status_code_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_fhir']
        definitions[0]['alerts']['status_codes'] = '401, 6xx'

        with pytest.raises(Exception) as context:
            _ = fhir_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert '6xx' in message
        assert _conn_name_1 in message

        # Nothing was written
        assert _stored(session, _conn_name_1) is None

# ################################################################################################################################

    def test_a_bad_outcome_code_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_fhir']

        # A SOAP fault code is not a FHIR issue code
        definitions[0]['alerts']['outcome_codes'] = 'exception, Receiver'

        with pytest.raises(Exception) as context:
            _ = fhir_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'Receiver' in message
        assert _conn_name_1 in message

        # Nothing was written
        assert _stored(session, _conn_name_1) is None

# ################################################################################################################################

    def test_a_soap_setting_is_rejected_on_a_fhir_connection(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_fhir']
        definitions[0]['alerts']['fault_codes'] = 'Receiver'

        with pytest.raises(Exception) as context:
            _ = fhir_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'fault_codes' in message
        assert _conn_name_1 in message

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingFHIRAlertsExport:

    def test_only_the_settings_moved_away_from_their_defaults_are_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
        fhir_exporter:'OutgoingFHIRExporter',
    ) -> 'None':
        _, _ = fhir_importer.sync_definitions(yaml_config['outgoing_fhir'], session)

        exported = fhir_exporter.export(session, _cluster_id)
        item = _by_name(exported)[_conn_name_1]

        expected = {
            'status_codes': _own_status_codes,
            'status_code_threshold': 5,
            'outcome_codes': _own_outcome_codes,
            'outcome_threshold': 5,
            'connection_failures': 2,
            'max_latency': 2500,
            'email_connection': f'smtp:{_smtp_name}',
            'llm_connection': _llm_name,
        }

        assert item[Alerts_Key] == expected
        assert list(item[Alerts_Key]) == list(expected)

        # The health check travels as how often it runs, never as its job ID, and the mapping is the last of the fields
        assert item[_health_check.Field_Run_Every] == _run_every
        assert item[_health_check.Field_Run_Unit] == _run_unit
        assert _health_check.Field_Job_ID not in item
        assert list(item)[-1] == Alerts_Key

        for key in item:
            assert not key.startswith('alert_')

        # A connection that moved nothing carries no alerts key and no health check
        item = _by_name(exported)[_conn_name_2]
        assert Alerts_Key not in item
        assert _health_check.Field_Run_Every not in item
        assert item['is_audit_log_active'] is False

# ################################################################################################################################

    def test_the_export_round_trips_through_the_writer(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
        fhir_exporter:'OutgoingFHIRExporter',
        tmp_path:'Path',
    ) -> 'None':
        _, _ = fhir_importer.sync_definitions(yaml_config['outgoing_fhir'], session)
        exported = fhir_exporter.export(session, _cluster_id)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'outgoing_fhir': exported})

        # The alerts mapping is the last field of a written connection, the codes quoted as the text they are
        written = path.read_text()
        assert f"    alerts:\n      status_codes: '{_own_status_codes}'\n      status_code_threshold: 5\n" in written
        assert f"      outcome_codes: '{_own_outcome_codes}'\n      outcome_threshold: 5\n" in written
        assert f'    health_check_run_every: {_run_every}\n    health_check_run_unit: {_run_unit}\n' in written

        read_back = yaml.safe_load(written)
        assert read_back['outgoing_fhir'] == exported

        # The same settings again store the same settings and export the same file
        _, _ = fhir_importer.sync_definitions(read_back['outgoing_fhir'], session)
        assert fhir_exporter.export(session, _cluster_id) == exported

# ################################################################################################################################
# ################################################################################################################################
