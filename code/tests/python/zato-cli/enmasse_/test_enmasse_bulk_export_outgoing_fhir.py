# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing FHIR connection's bulk_export mapping - imported into the bulk_export_ opaque keys next to the connection's
# own fields, the lists stored one value per line and the destinations as the text the Dashboard writes, a schedule creating
# its job as a FHIR one, an unknown field and a job id refused, an update making the file the source of truth, and the export
# writing the mapping back only when the export is on or configured, never with its job id.

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
from zato.common.api import GENERIC, HL7, HTTP_SOAP, SchedulerLink
from zato.common.destination.model import parse_entries
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, IntervalBasedJob, Job, \
    SecurityBase, Service

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

_bulk = HL7.BulkExport
_health_check = HTTP_SOAP.HealthCheck
_fhir_type = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR

# The cluster every object in the test database belongs to
_cluster_id = 1

# The connections of the file - one with a scheduled group export, one with nothing
_conn_name_1 = 'enmasse.bulk.fhir.conn.1'
_conn_name_2 = 'enmasse.bulk.fhir.conn.2'

_address_1 = 'https://ehr.example.com/fhir/r4'
_address_2 = 'https://lab.example.com/fhir/r4'

# What the first connection exports
_group_id = 'diabetes-registry'
_types = ['Patient', 'Observation']
_since = '2026-01-01T00:00:00Z'
_type_filter = ['Observation?category=laboratory']

# How often the first connection exports - the start date lies ahead so the job keeps it as it is
_run_every = 6
_run_unit = 'hours'
_start_date = '2036-01-02T03:00:00'

# Where the files go
_sftp_name = 'enmasse.bulk.fhir.sftp'
_kafka_name = 'enmasse.bulk.fhir.kafka'
_remote_path = '/exports/{job_id}/{file_name}'

_yaml_text = f"""
outgoing_fhir:
  - name: {_conn_name_1}
    address: {_address_1}
    bulk_export:
      is_active: true
      level: group
      group_id: {_group_id}
      types:
        - {_types[0]}
        - {_types[1]}
      since: "{_since}"
      type_filter:
        - "{_type_filter[0]}"
      run_every: {_run_every}
      run_unit: {_run_unit}
      start_date: "{_start_date}"
      delete_on_server: false
      destinations:
        - name: {_sftp_name}
          type: sftp
          connection: {_sftp_name}
          options:
            remote_path: {_remote_path}
        - name: {_kafka_name}
          type: kafka
          connection: {_kafka_name}
          is_active: false

  - name: {_conn_name_2}
    address: {_address_2}
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
    """ A real ODB session over an in-memory SQLite database holding one cluster and the service a bulk export job invokes.
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

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

    session.add(Service(None, _bulk.Dispatch_Service, True, 'zato.server.service.internal.hl7.fhir.bulk_export.Run',
        True, cluster))

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

class TestOutgoingFHIRBulkExportImport:

    def test_the_mapping_is_stored_flat_under_its_prefix(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        created, _ = fhir_importer.sync_definitions(yaml_config['outgoing_fhir'], session)
        connection = _by_name(created)[_conn_name_1]

        opaque = _opaque(connection)

        assert opaque[_bulk.Field_Is_Active] is True
        assert opaque[_bulk.Field_Level] == _bulk.Level.Group
        assert opaque[_bulk.Field_Group_ID] == _group_id
        assert opaque[_bulk.Field_Since] == _since
        assert opaque[_bulk.Field_Delete_On_Server] is False

        # The lists are stored one value per line ..
        assert opaque[_bulk.Field_Types] == '\n'.join(_types)
        assert opaque[_bulk.Field_Type_Filter] == '\n'.join(_type_filter)

        # .. the destinations as the text the Dashboard writes ..
        entries = parse_entries(opaque[_bulk.Field_Destinations])
        assert len(entries) == 2

        sftp, kafka = entries
        assert sftp.type == 'sftp'
        assert sftp.connection == _sftp_name
        assert sftp.is_active is True
        assert sftp.options == {'remote_path': _remote_path}

        assert kafka.type == 'kafka'
        assert kafka.connection == _kafka_name
        assert kafka.is_active is False
        assert kafka.options == {}

        # .. what the mapping left out is at its default ..
        assert opaque[_bulk.Field_Patient_IDs] == ''
        assert opaque[_bulk.Field_Delete_Files] is True

        # .. and the mapping itself is not stored.
        assert _bulk.Enmasse_Key not in opaque
        assert connection.address == _address_1

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

        assert opaque[_bulk.Field_Is_Active] is False
        assert opaque[_bulk.Field_Level] == _bulk.Level.Group
        assert opaque[_bulk.Field_Types] == ''
        assert opaque[_bulk.Field_Destinations] == ''
        assert opaque[_bulk.Field_Run_Every] == ''
        assert opaque[_bulk.Field_Job_ID] == ''

        # No schedule was asked for, so no job exists for it
        assert session.query(Job).filter_by(name=_bulk.Job_Prefix + _conn_name_2).first() is None

# ################################################################################################################################

    def test_a_schedule_creates_its_job_as_a_fhir_one(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        created, _ = fhir_importer.sync_definitions(yaml_config['outgoing_fhir'], session)
        connection = _by_name(created)[_conn_name_1]

        # The job exists, named after the connection, invoking the run service on the schedule asked for ..
        job = session.query(Job).filter_by(name=_bulk.Job_Prefix + _conn_name_1).one()
        assert job.service.name == _bulk.Dispatch_Service
        assert job.is_active is True
        assert job.interval_based.hours == _run_every
        assert job.start_date.replace(tzinfo=None).isoformat() == _start_date

        job_opaque = loads(job.opaque1)
        assert job_opaque[SchedulerLink.Conn_Type] == SchedulerLink.ConnType.FHIR_Outgoing
        assert job_opaque[SchedulerLink.Conn_ID] == connection.id
        assert job_opaque[SchedulerLink.Kind] == SchedulerLink.KindType.BulkExport

        extra = loads(job.extra)
        assert extra == {
            _health_check.Extra_Conn_ID: connection.id,
            _health_check.Extra_Conn_Name: _conn_name_1,
            _health_check.Extra_Conn_Type: SchedulerLink.ConnType.FHIR_Outgoing,
        }

        # .. and the connection remembers the job and how often it runs.
        opaque = _opaque(connection)
        assert opaque[_bulk.Field_Run_Every] == _run_every
        assert opaque[_bulk.Field_Run_Unit] == _run_unit
        assert opaque[_bulk.Field_Job_ID] == job.id

        # The same file again finds the job by its name rather than creating another
        _, _ = fhir_importer.sync_definitions(yaml.safe_load(_yaml_text)['outgoing_fhir'], session)
        assert session.query(Job).filter_by(name=_bulk.Job_Prefix + _conn_name_1).count() == 1

# ################################################################################################################################

    def test_an_inactive_export_keeps_its_job_inactive(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_fhir']
        definitions[0]['bulk_export']['is_active'] = False

        _, _ = fhir_importer.sync_definitions(definitions, session)

        job = session.query(Job).filter_by(name=_bulk.Job_Prefix + _conn_name_1).one()
        assert job.is_active is False

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        created, _ = fhir_importer.sync_definitions(yaml_config['outgoing_fhir'], session)
        assert len(created) == 2

        # A smaller mapping resets what it left out to the defaults
        definitions = yaml.safe_load(_yaml_text)['outgoing_fhir']
        definitions[0]['bulk_export'] = {'is_active': True, 'level': 'system', 'run_every': 1, 'run_unit': 'days'}

        created_again, updated = fhir_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0

        connection = _by_name(updated)[_conn_name_1]
        opaque = _opaque(connection)

        assert opaque[_bulk.Field_Level] == _bulk.Level.System
        assert opaque[_bulk.Field_Group_ID] == ''
        assert opaque[_bulk.Field_Types] == ''
        assert opaque[_bulk.Field_Destinations] == ''
        assert opaque[_bulk.Field_Delete_On_Server] is True

        job = session.query(Job).filter_by(name=_bulk.Job_Prefix + _conn_name_1).one()
        assert job.interval_based.days == 1
        assert opaque[_bulk.Field_Job_ID] == job.id

# ################################################################################################################################

    def test_an_unknown_field_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_fhir']
        definitions[0]['bulk_export']['cron'] = '0 3 * * *'

        with pytest.raises(Exception) as context:
            _ = fhir_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'cron' in message
        assert _conn_name_1 in message

        # Nothing was written
        assert _stored(session, _conn_name_1) is None

# ################################################################################################################################

    def test_a_job_id_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_fhir']
        definitions[0]['bulk_export']['job_id'] = 123

        with pytest.raises(Exception) as context:
            _ = fhir_importer.sync_definitions(definitions, session)

        assert 'job_id' in str(context.value)

# ################################################################################################################################

    def test_a_destination_of_an_unknown_type_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        fhir_importer:'OutgoingFHIRImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_fhir']
        definitions[0]['bulk_export']['destinations'][0]['type'] = 'carrier-pigeon'

        with pytest.raises(Exception) as context:
            _ = fhir_importer.sync_definitions(definitions, session)

        assert 'carrier-pigeon' in str(context.value)

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingFHIRBulkExportExport:

    def test_the_mapping_is_written_back_without_its_job_id(
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
            'is_active': True,
            'group_id': _group_id,
            'types': _types,
            'since': _since,
            'type_filter': _type_filter,
            'run_every': _run_every,
            'run_unit': _run_unit,
            'start_date': _start_date,
            'destinations': [
                {'name': _sftp_name, 'type': 'sftp', 'connection': _sftp_name, 'is_active': True,
                    'options': {'remote_path': _remote_path}},
                {'name': _kafka_name, 'type': 'kafka', 'connection': _kafka_name, 'is_active': False},
            ],
            'delete_on_server': False,
        }

        assert item[_bulk.Enmasse_Key] == expected
        assert 'job_id' not in item[_bulk.Enmasse_Key]

        # None of the flat fields reach the file
        for key in item:
            assert not key.startswith(_bulk.Field_Prefix)

        # A connection that moved nothing carries no mapping at all
        item = _by_name(exported)[_conn_name_2]
        assert _bulk.Enmasse_Key not in item

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

        written = path.read_text()
        assert f'    bulk_export:\n      is_active: true\n      group_id: {_group_id}\n' in written
        assert f'      types:\n        - {_types[0]}\n        - {_types[1]}\n' in written
        assert f'      destinations:\n        - name: {_sftp_name}\n          type: sftp\n' in written

        read_back = yaml.safe_load(written)
        assert read_back['outgoing_fhir'] == exported

        # The same settings again store the same settings and export the same file
        _, _ = fhir_importer.sync_definitions(read_back['outgoing_fhir'], session)
        assert fhir_exporter.export(session, _cluster_id) == exported

# ################################################################################################################################
# ################################################################################################################################
