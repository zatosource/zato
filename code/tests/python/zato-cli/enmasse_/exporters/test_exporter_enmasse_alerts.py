# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from pathlib import Path

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
from zato.cli.enmasse.exporters.ftp import FTPExporter
from zato.cli.enmasse.exporters.sftp import SFTPExporter
from zato.cli.enmasse.exporters.smb import SMBExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.cli.enmasse.importers.ftp import FTPImporter
from zato.cli.enmasse.importers.sftp import SFTPImporter
from zato.cli.enmasse.importers.smb import SMBImporter
from zato.cli.enmasse.util import FileWriter
from zato.common.alerting.object_config import Alerts_Key
from zato.common.api import EMAIL, GENERIC
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, HTTPSOAP, SecurityBase, Service, SMTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_
    anydict = anydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The cluster every object in the test database belongs to
_cluster_id = 1

# The SMTP connection the alerts mappings name
_smtp_name = 'enmasse.alerts.export.smtp'

# The LLM connection the first connection names for its explanations
_llm_name = 'enmasse.alerts.export.llm'

# The service the REST channels invoke
_service_name = 'enmasse.alerts.export.service'

# One connection moving every alert setting away from its default, one moving a few of them
# and one carrying no alerts mapping at all - the last one exports without the key.
_yaml_text = f"""
sftp:
  - name: enmasse.alerts.export.sftp.1
    address: sftp.example.com
    username: enmasse
    alerts:
      is_active: false
      consecutive_failures: 5
      warning_failures: 15
      error_failures: 30
      window: 43200
      arrival_overdue: 2
      test_transfers: true
      use_llm: false
      email_connection: smtp:{_smtp_name}
      llm_connection: {_llm_name}

  - name: enmasse.alerts.export.sftp.2
    address: sftp.example.com
    username: enmasse
    alerts:
      error_failures: 25
      email_connection: smtp:{_smtp_name}

  - name: enmasse.alerts.export.sftp.3
    address: sftp.example.com
    username: enmasse

ftp:
  - name: enmasse.alerts.export.ftp.1
    host: ftp.example.com
    alerts:
      consecutive_failures: 7

smb:
  - name: enmasse.alerts.export.smb.1
    host: smb.example.com
    alerts:
      window: 3600

channel_rest:
  - name: enmasse.alerts.export.channel.1
    service: {_service_name}
    url_path: /enmasse/alerts/export/channel/1
    alerts:
      max_latency: 2000
      traffic_expected: true
      silence_window: 1800
      email_connection: smtp:{_smtp_name}
      llm_connection: {_llm_name}

  - name: enmasse.alerts.export.channel.2
    service: {_service_name}
    url_path: /enmasse/alerts/export/channel/2
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
    """ A real ODB session over an in-memory SQLite database holding one cluster,
    the generic connection tables and the SMTP connection the alerts mappings name.
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

    service = Service(None, _service_name, True, 'enmasse.alerts.export.Service', False, cluster)
    session.add(service)

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
def importer() -> 'EnmasseYAMLImporter':
    out = EnmasseYAMLImporter()
    return out

# ################################################################################################################################

@pytest.fixture
def exporter() -> 'EnmasseYAMLExporter':
    out = EnmasseYAMLExporter()
    return out

# ################################################################################################################################

def _by_name(items:'any_') -> 'anydict':
    out = {}

    for item in items:
        out[item['name']] = item

    return out

# ################################################################################################################################

def _import_and_export(
    yaml_config:'stranydict',
    session:'any_',
    importer:'EnmasseYAMLImporter',
    exporter:'EnmasseYAMLExporter',
) -> 'stranydict':
    """ Imports what the file declares and answers with the export of each section, keyed by section name.
    """
    _, _ = SFTPImporter(importer).sync_definitions(yaml_config['sftp'], session)
    _, _ = FTPImporter(importer).sync_definitions(yaml_config['ftp'], session)
    _, _ = SMBImporter(importer).sync_definitions(yaml_config['smb'], session)
    _, _ = ChannelImporter(importer).sync_channel_rest(yaml_config['channel_rest'], session)

    out = {
        'sftp': SFTPExporter(exporter).export(session, _cluster_id),
        'ftp': FTPExporter(exporter).export(session, _cluster_id),
        'smb': SMBExporter(exporter).export(session, _cluster_id),
        'channel_rest': ChannelExporter(exporter).export(session, _cluster_id),
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAlertsExport:

    def test_every_setting_moved_away_from_its_default_is_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        importer:'EnmasseYAMLImporter',
        exporter:'EnmasseYAMLExporter',
    ) -> 'None':
        """ A connection that moved every alert setting has every one of them in its alerts mapping,
        in field order, under the names the file gives them.
        """
        exported = _import_and_export(yaml_config, session, importer, exporter)
        item = _by_name(exported['sftp'])['enmasse.alerts.export.sftp.1']

        expected = {
            'is_active': False,
            'consecutive_failures': 5,
            'warning_failures': 15,
            'error_failures': 30,
            'window': 43200,
            'arrival_overdue': 2,
            'test_transfers': True,
            'use_llm': False,
            'email_connection': f'smtp:{_smtp_name}',
            'llm_connection': _llm_name,
        }

        assert item[Alerts_Key] == expected
        assert list(item[Alerts_Key]) == list(expected)

        # The flat storage names never reach the file
        for key in item:
            assert not key.startswith('alert_')

# ################################################################################################################################

    def test_settings_at_their_defaults_are_not_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        importer:'EnmasseYAMLImporter',
        exporter:'EnmasseYAMLExporter',
    ) -> 'None':
        """ Only what a connection was configured away from is written, so a file this export produces
        reads the way one written by hand does.
        """
        exported = _import_and_export(yaml_config, session, importer, exporter)
        item = _by_name(exported['sftp'])['enmasse.alerts.export.sftp.2']

        expected = {
            'error_failures': 25,
            'email_connection': f'smtp:{_smtp_name}',
        }
        assert item[Alerts_Key] == expected

# ################################################################################################################################

    def test_a_connection_on_defaults_has_no_alerts_key(
        self,
        yaml_config:'stranydict',
        session:'any_',
        importer:'EnmasseYAMLImporter',
        exporter:'EnmasseYAMLExporter',
    ) -> 'None':
        """ A connection that moved nothing carries no alerts key at all.
        """
        exported = _import_and_export(yaml_config, session, importer, exporter)
        item = _by_name(exported['sftp'])['enmasse.alerts.export.sftp.3']

        assert Alerts_Key not in item

# ################################################################################################################################

    def test_ftp_and_smb_export_the_same_way(
        self,
        yaml_config:'stranydict',
        session:'any_',
        importer:'EnmasseYAMLImporter',
        exporter:'EnmasseYAMLExporter',
    ) -> 'None':
        """ FTP and SMB connections export their alert settings the way SFTP ones do.
        """
        exported = _import_and_export(yaml_config, session, importer, exporter)

        item = _by_name(exported['ftp'])['enmasse.alerts.export.ftp.1']
        assert item[Alerts_Key] == {'consecutive_failures': 7}

        item = _by_name(exported['smb'])['enmasse.alerts.export.smb.1']
        assert item[Alerts_Key] == {'window': 3600}

# ################################################################################################################################

    def test_the_export_round_trips_through_the_writer(
        self,
        yaml_config:'stranydict',
        session:'any_',
        importer:'EnmasseYAMLImporter',
        exporter:'EnmasseYAMLExporter',
        tmp_path:'Path',
    ) -> 'None':
        """ What the export produces is written as a nested alerts mapping and reads back as the same values,
        which is what makes an exported file importable as it is.
        """
        exported = _import_and_export(yaml_config, session, importer, exporter)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write(exported)

        written = path.read_text()
        assert '    alerts:\n      is_active: ' in written
        assert '      consecutive_failures: 5\n' in written

        read_back = yaml.safe_load(written)

        for section in ['sftp', 'ftp', 'smb', 'channel_rest']:
            assert read_back[section] == exported[section]

# ################################################################################################################################
# ################################################################################################################################

class TestChannelAlertsExport:

    def test_only_the_settings_moved_away_from_their_defaults_are_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        importer:'EnmasseYAMLImporter',
        exporter:'EnmasseYAMLExporter',
    ) -> 'None':
        """ A REST channel's alerts mapping carries what the channel was configured away from, in field order,
        durations in seconds, and the flat storage names never reach the file.
        """
        exported = _import_and_export(yaml_config, session, importer, exporter)
        item = _by_name(exported['channel_rest'])['enmasse.alerts.export.channel.1']

        expected = {
            'max_latency': 2000,
            'traffic_expected': True,
            'silence_window': 1800,
            'email_connection': f'smtp:{_smtp_name}',
            'llm_connection': _llm_name,
        }

        assert item[Alerts_Key] == expected
        assert list(item[Alerts_Key]) == list(expected)

        for key in item:
            assert not key.startswith('alert_')

# ################################################################################################################################

    def test_a_channel_on_defaults_has_no_alerts_key(
        self,
        yaml_config:'stranydict',
        session:'any_',
        importer:'EnmasseYAMLImporter',
        exporter:'EnmasseYAMLExporter',
    ) -> 'None':
        """ A REST channel that moved nothing carries no alerts key, whatever else it carries.
        """
        exported = _import_and_export(yaml_config, session, importer, exporter)
        item = _by_name(exported['channel_rest'])['enmasse.alerts.export.channel.2']

        assert Alerts_Key not in item
        assert item['is_audit_log_active'] is False

# ################################################################################################################################

    def test_the_channel_export_round_trips_through_the_writer(
        self,
        yaml_config:'stranydict',
        session:'any_',
        importer:'EnmasseYAMLImporter',
        exporter:'EnmasseYAMLExporter',
        tmp_path:'Path',
    ) -> 'None':
        """ The alerts mapping is the last field of a written channel and what is written imports back
        into the very same stored settings.
        """
        exported = _import_and_export(yaml_config, session, importer, exporter)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'channel_rest': exported['channel_rest']})

        written = path.read_text()
        assert '    url_path: /enmasse/alerts/export/channel/1\n    alerts:\n      max_latency: 2000\n' in written

        read_back = yaml.safe_load(written)
        assert read_back['channel_rest'] == exported['channel_rest']

        # The same settings again change nothing
        _, updated = ChannelImporter(importer).sync_channel_rest(read_back['channel_rest'], session)
        assert len(updated) == 0

# ################################################################################################################################
# ################################################################################################################################
